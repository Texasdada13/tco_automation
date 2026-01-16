#!/usr/bin/env python3
"""
Product Match Review CLI Tool

Interactive command-line tool for reviewing and approving product matches
that couldn't be automatically resolved by the ProductMatcher.

Usage:
    python review_matches.py                    # Review pending items
    python review_matches.py --stats            # Show queue statistics
    python review_matches.py --export           # Export unmatched to CSV
    python review_matches.py --load FILE.json   # Load extractions and find unmatched

The review workflow:
1. Load extracted JSON files or a review queue
2. Present unmatched products one at a time
3. User decides: accept suggestion, pick category, create new, or skip
4. Approved matches are automatically added to the ontology
5. All decisions are logged for audit trail
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.product_matcher import MatchMethod, MatchResult, ProductMatcher


class ReviewQueue:
    """Manages the queue of items needing human review."""

    def __init__(self, queue_path: Optional[str] = None):
        if queue_path is None:
            base_dir = Path(__file__).parent
            queue_path = base_dir / "ontology" / "review_queue.json"
        self.queue_path = Path(queue_path)
        self.audit_path = self.queue_path.parent / "review_audit_log.json"

        self.pending_items = []
        self.completed_items = []
        self.skipped_items = []
        self._load_queue()

    def _load_queue(self) -> None:
        """Load existing queue from disk."""
        if self.queue_path.exists():
            try:
                with open(self.queue_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.pending_items = data.get('pending_items', [])
                self.completed_items = data.get('completed_items', [])
                self.skipped_items = data.get('skipped_items', [])
            except (json.JSONDecodeError, IOError):
                pass

    def save_queue(self) -> None:
        """Save queue to disk."""
        data = {
            'queue_metadata': {
                'last_updated': datetime.now().isoformat(),
                'pending_count': len(self.pending_items),
                'completed_count': len(self.completed_items),
                'skipped_count': len(self.skipped_items)
            },
            'pending_items': self.pending_items,
            'completed_items': self.completed_items,
            'skipped_items': self.skipped_items
        }

        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def add_item(self, result: MatchResult, source_file: str = "") -> None:
        """Add an unmatched item to the review queue."""
        # Check if already in queue
        for item in self.pending_items:
            if (item['original_name'] == result.original_name and
                item['vendor'] == result.vendor):
                return  # Already in queue

        item = {
            'item_id': f"review_{len(self.pending_items) + len(self.completed_items):04d}",
            'created_at': datetime.now().isoformat(),
            'original_name': result.original_name,
            'vendor': result.vendor,
            'source_file': source_file,
            'match_method': result.match_method.value,
            'fuzzy_suggestion': {
                'category': result.canonical_category,
                'name': result.canonical_name,
                'confidence': result.confidence,
                'matched_term': result.matched_term
            } if result.match_method == MatchMethod.FUZZY else None,
            'skip_count': 0
        }
        self.pending_items.append(item)

    def get_next_item(self) -> Optional[dict]:
        """Get the next item to review."""
        if not self.pending_items:
            return None
        return self.pending_items[0]

    def complete_item(self, item_id: str, decision: str, category_key: str = None,
                      reviewer: str = "user") -> None:
        """Mark an item as completed."""
        for i, item in enumerate(self.pending_items):
            if item['item_id'] == item_id:
                completed = self.pending_items.pop(i)
                completed['completed_at'] = datetime.now().isoformat()
                completed['decision'] = decision
                completed['assigned_category'] = category_key
                completed['reviewer'] = reviewer
                self.completed_items.append(completed)
                self._log_audit(completed)
                return

    def skip_item(self, item_id: str) -> None:
        """Skip an item (move to end of queue)."""
        for i, item in enumerate(self.pending_items):
            if item['item_id'] == item_id:
                item['skip_count'] = item.get('skip_count', 0) + 1
                if item['skip_count'] >= 3:
                    # Move to skipped after 3 skips
                    skipped = self.pending_items.pop(i)
                    skipped['skipped_at'] = datetime.now().isoformat()
                    self.skipped_items.append(skipped)
                else:
                    # Move to end of queue
                    self.pending_items.append(self.pending_items.pop(i))
                return

    def _log_audit(self, completed_item: dict) -> None:
        """Log the review decision to audit log."""
        audit_entry = {
            'audit_id': f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'item_id': completed_item['item_id'],
            'original_name': completed_item['original_name'],
            'vendor': completed_item['vendor'],
            'decision': completed_item['decision'],
            'assigned_category': completed_item.get('assigned_category'),
            'reviewer': completed_item.get('reviewer', 'unknown')
        }

        # Load existing audit log
        audit_data = {'audit_entries': []}
        if self.audit_path.exists():
            try:
                with open(self.audit_path, 'r', encoding='utf-8') as f:
                    audit_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        audit_data['audit_entries'].append(audit_entry)

        with open(self.audit_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)

    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            'pending': len(self.pending_items),
            'completed': len(self.completed_items),
            'skipped': len(self.skipped_items),
            'total_reviewed': len(self.completed_items) + len(self.skipped_items)
        }


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


def print_header(text: str):
    """Print a styled header."""
    width = 70
    print("=" * width)
    print(f" {text}")
    print("=" * width)


def print_categories(matcher: ProductMatcher):
    """Print available categories for selection."""
    categories = matcher.get_all_categories()
    print("\nAvailable Categories:")
    print("-" * 50)

    # Group by first letter for easier navigation
    for i, cat_key in enumerate(sorted(categories), 1):
        cat_info = matcher.get_category_info(cat_key)
        name = cat_info.get('canonical_name', cat_key)
        print(f"  {i:2}. {name}")

    return sorted(categories)


def review_item(item: dict, matcher: ProductMatcher, queue: ReviewQueue) -> bool:
    """
    Interactive review of a single item.

    Returns True to continue reviewing, False to exit.
    """
    clear_screen()
    print_header("PRODUCT MATCH REVIEW")
    print()
    print(f"Product:  {item['original_name']}")
    print(f"Vendor:   {item['vendor']}")
    if item.get('source_file'):
        print(f"Source:   {item['source_file']}")
    print(f"Skipped:  {item.get('skip_count', 0)} time(s)")
    print()

    # Show fuzzy suggestion if available
    if item.get('fuzzy_suggestion') and item['fuzzy_suggestion'].get('category'):
        suggestion = item['fuzzy_suggestion']
        print("-" * 50)
        print("SUGGESTED MATCH:")
        print(f"  Category:   {suggestion['name']}")
        print(f"  Confidence: {suggestion['confidence']:.0f}%")
        print(f"  Based on:   {suggestion['matched_term']}")
        print("-" * 50)
        print()

    # Show options
    print("Options:")
    print("  [A] Accept suggestion (if available)")
    print("  [C] Choose from category list")
    print("  [N] Create new category (not yet implemented)")
    print("  [S] Skip (review later)")
    print("  [Q] Quit review session")
    print()

    while True:
        choice = input("Your choice: ").strip().upper()

        if choice == 'Q':
            return False

        elif choice == 'S':
            queue.skip_item(item['item_id'])
            queue.save_queue()
            print("Skipped. Moving to next item...")
            return True

        elif choice == 'A':
            if item.get('fuzzy_suggestion') and item['fuzzy_suggestion'].get('category'):
                category_key = item['fuzzy_suggestion']['category']
                # Add term to ontology
                matcher.add_term_to_ontology(
                    category_key=category_key,
                    vendor=item['vendor'],
                    new_term=item['original_name']
                )
                queue.complete_item(
                    item['item_id'],
                    decision='accepted_suggestion',
                    category_key=category_key
                )
                queue.save_queue()
                print(f"Accepted! Added '{item['original_name']}' to {item['fuzzy_suggestion']['name']}")
                input("Press Enter to continue...")
                return True
            else:
                print("No suggestion available. Use [C] to choose a category.")

        elif choice == 'C':
            categories = print_categories(matcher)
            print()
            cat_choice = input("Enter category number (or 'b' to go back): ").strip()

            if cat_choice.lower() == 'b':
                continue

            try:
                cat_index = int(cat_choice) - 1
                if 0 <= cat_index < len(categories):
                    category_key = categories[cat_index]
                    cat_info = matcher.get_category_info(category_key)

                    # Add term to ontology
                    matcher.add_term_to_ontology(
                        category_key=category_key,
                        vendor=item['vendor'],
                        new_term=item['original_name']
                    )
                    queue.complete_item(
                        item['item_id'],
                        decision='manual_selection',
                        category_key=category_key
                    )
                    queue.save_queue()
                    print(f"Added '{item['original_name']}' to {cat_info['canonical_name']}")
                    input("Press Enter to continue...")
                    return True
                else:
                    print("Invalid category number.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == 'N':
            print("Create new category feature coming soon.")
            print("For now, please add new categories directly to product_ontology.yaml")
            input("Press Enter to continue...")

        else:
            print("Invalid choice. Please try again.")


def load_extractions_to_queue(json_path: str, matcher: ProductMatcher, queue: ReviewQueue):
    """Load an extraction JSON and add unmatched items to the queue."""
    path = Path(json_path)

    if path.is_dir():
        files = list(path.glob("*_extraction_ai.json"))
    else:
        files = [path]

    total_added = 0

    for file_path in files:
        print(f"Processing: {file_path.name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        vendor = data.get('vendor', 'UNKNOWN')
        line_items = data.get('line_items', [])

        for item in line_items:
            item['vendor'] = vendor

        results = matcher.match_batch(line_items)

        for item, result in zip(line_items, results):
            if result.needs_review:
                queue.add_item(result, source_file=file_path.name)
                total_added += 1

    queue.save_queue()
    print(f"\nAdded {total_added} items to review queue.")


def show_stats(queue: ReviewQueue, matcher: ProductMatcher):
    """Show queue and ontology statistics."""
    stats = queue.get_stats()
    categories = matcher.get_all_categories()

    print_header("REVIEW QUEUE STATISTICS")
    print()
    print(f"Pending reviews:     {stats['pending']}")
    print(f"Completed reviews:   {stats['completed']}")
    print(f"Skipped (3+ times):  {stats['skipped']}")
    print(f"Total processed:     {stats['total_reviewed']}")
    print()
    print(f"Ontology categories: {len(categories)}")
    print()

    if stats['pending'] > 0:
        print("Top pending items:")
        for item in queue.pending_items[:5]:
            print(f"  - [{item['vendor']}] {item['original_name']}")


def export_unmatched(queue: ReviewQueue, output_path: str = "unmatched_products.csv"):
    """Export unmatched products to CSV."""
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Vendor', 'Product Name', 'Source File', 'Skip Count', 'Status'])

        for item in queue.pending_items:
            writer.writerow([
                item['vendor'],
                item['original_name'],
                item.get('source_file', ''),
                item.get('skip_count', 0),
                'pending'
            ])

        for item in queue.skipped_items:
            writer.writerow([
                item['vendor'],
                item['original_name'],
                item.get('source_file', ''),
                item.get('skip_count', 0),
                'skipped'
            ])

    print(f"Exported {len(queue.pending_items) + len(queue.skipped_items)} items to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Review and approve product matches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python review_matches.py                     Start interactive review
  python review_matches.py --stats             Show queue statistics
  python review_matches.py --load "Extracted JSON"  Load extractions
  python review_matches.py --export            Export unmatched to CSV
        """
    )
    parser.add_argument('--stats', action='store_true', help='Show queue statistics')
    parser.add_argument('--load', type=str, help='Load extraction JSON file or directory')
    parser.add_argument('--export', action='store_true', help='Export unmatched to CSV')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI suggestions')

    args = parser.parse_args()

    # Initialize
    matcher = ProductMatcher(enable_ai=not args.no_ai)
    queue = ReviewQueue()

    print()
    print("Product Match Review Tool")
    print(f"AI suggestions: {'disabled' if args.no_ai else 'enabled (default)'}")
    print()

    if args.load:
        load_extractions_to_queue(args.load, matcher, queue)
        return

    if args.stats:
        show_stats(queue, matcher)
        return

    if args.export:
        export_unmatched(queue)
        return

    # Interactive review mode
    stats = queue.get_stats()
    if stats['pending'] == 0:
        print("No items pending review!")
        print()
        print("To add items to the queue, run:")
        print('  python review_matches.py --load "Extracted JSON"')
        return

    print(f"Found {stats['pending']} items pending review.")
    print()
    input("Press Enter to start reviewing...")

    while True:
        item = queue.get_next_item()
        if item is None:
            print("\nAll items reviewed! Great job.")
            break

        if not review_item(item, matcher, queue):
            print("\nReview session ended.")
            break

    # Final stats
    print()
    show_stats(queue, matcher)


if __name__ == "__main__":
    main()
