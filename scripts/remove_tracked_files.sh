#!/bin/bash
set -euo pipefail

# Safe removal script: stops tracking db.sqlite3 and data.json on listed branches
# Usage: run from a clean clone (no uncommitted changes). It will keep local copies
# of the files and only remove them from the Git index, commit, and push the change.

BRANCHES=(
  "main"
  "feature/offers"
  "feature/banner"
  "feature/orders"
  "feature/reviews"
  "feature/cart"
  "feature/wishlist"
  "feature/product-category"
  "feature/authentication"
  "feature/payments"
  "feature/coupons"
)

FILES=("db.sqlite3" "data.json")

echo "This will remove tracking of: ${FILES[*]}\nfrom branches: ${BRANCHES[*]}"
read -p "Continue? (y/N) " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted by user"
  exit 1
fi

# Ensure we have a clean working tree
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Please commit or stash your local changes before running this script." >&2
  exit 1
fi

for b in "${BRANCHES[@]}"; do
  echo "\n--- Processing branch: $b ---"
  # Fetch and ensure branch exists locally
  git fetch origin "$b":"refs/remotes/origin/$b" || true
  if ! git show-ref --verify --quiet "refs/remotes/origin/$b"; then
    echo "Branch $b does not exist on origin, skipping."
    continue
  fi

  # Create or update a local tracking branch
  if git show-ref --verify --quiet "refs/heads/$b"; then
    git checkout "$b"
    git reset --hard "origin/$b"
  else
    git checkout -b "$b" "origin/$b"
  fi

  removed=false
  for f in "${FILES[@]}"; do
    if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
      echo "Removing $f from index on $b"
      git rm --cached -f "$f" || true
      removed=true
    else
      echo "$f not tracked on $b"
    fi
  done

  if [ "$removed" = true ]; then
    # Only commit if there are staged changes
    if ! git diff --cached --quiet; then
      git commit -m "Stop tracking db.sqlite3 and data.json (now in .gitignore)"
      git push origin "$b"
      echo "Pushed removal commit to $b"
    else
      echo "No staged changes to commit on $b"
    fi
  else
    echo "Nothing to remove on $b"
  fi

done

echo "\nDone. Verify each branch on GitHub. If you want these files removed from history, run a history-rewrite tool like git-filter-repo or BFG (instructions in README)."