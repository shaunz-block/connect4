"""
Alpha-Beta Pruning — interactive visualizer

Tree structure:
             A  [MAX]
            /        \\
        B [MIN]     C [MIN]
        / | \\       / | \\
       b1  b2  b3  c1  c2  c3
"""

# @visualize color — ANSI terminal decorators
RESET = "\033[0m"
RED = "\033[31m"  # pruned
GREEN = "\033[32m"  # result / chosen
YELLOW = "\033[33m"  # alpha (MAX's best guarantee)
MAGENTA = "\033[35m"  # beta  (MIN's best guarantee)
CYAN = "\033[36m"  # currently visiting
GRAY = "\033[90m"  # extra info
BOLD = "\033[1m"


class Node:
    def __init__(self, label, leaf_val=None, children=None):
        self.label = label
        self.leaf_val = leaf_val  # int if leaf, else None
        self.children = children or []
        self.result = None  # filled during search
        self.pruned = False

    def is_leaf(self):
        return self.leaf_val is not None


def search(node, is_max, alpha, beta, depth=0):
    pad = "  " * depth
    a_str = "-∞" if alpha == float("-inf") else str(alpha)
    b_str = "+∞" if beta == float("inf") else str(beta)

    # ── Leaf ──────────────────────────────────────────────────────────────
    if node.is_leaf():
        node.result = node.leaf_val
        # @visualize color *node GREEN
        print(f"{pad}{GREEN}● leaf {node.label}  →  {node.leaf_val}{RESET}")
        return node.leaf_val

    # ── Internal node ──────────────────────────────────────────────────────
    # @visualize color *node CYAN  alpha  beta
    print(f"{pad}{CYAN}▶ {node.label}  [α={YELLOW}{a_str}{CYAN}  β={MAGENTA}{b_str}{CYAN}]{RESET}")

    best = float("-inf") if is_max else float("inf")

    for i, child in enumerate(node.children):
        score = search(child, not is_max, alpha, beta, depth + 1)
        child.result = score

        if is_max:
            if score > best:
                best = score
            if score > alpha:
                alpha = score
                # @visualize color alpha YELLOW
                print(f"{pad}  {YELLOW}↑ α updated → {alpha}{RESET}")
        else:
            if score < best:
                best = score
            if score < beta:
                beta = score
                # @visualize color beta MAGENTA
                print(f"{pad}  {MAGENTA}↓ β updated → {beta}{RESET}")

        # ── Pruning condition ────────────────────────────────────────────
        if alpha >= beta:
            for pruned_child in node.children[i + 1 :]:
                _mark_pruned(pruned_child)
                # @visualize color *node RED pruned
                print(
                    f"{pad}  {RED}✂ PRUNE {pruned_child.label}"
                    f"  (α={YELLOW}{alpha}{RED} ≥ β={MAGENTA}{beta}{RED}){RESET}"
                )
            print(
                f"{pad}{GRAY}  └─ MAX already has α={alpha}; "
                f"MIN won't pick anything ≥{alpha} because β={beta} ≤ α.{RESET}"
            )
            break

    node.result = best
    # @visualize color *node GREEN result
    print(f"{pad}{GREEN}◀ {node.label}  returns  {best}{RESET}")
    return best


def _mark_pruned(node):
    node.pruned = True
    for child in node.children:
        _mark_pruned(child)


def print_tree(node, prefix="", last=True):
    connector = "└── " if last else "├── "
    print(prefix + connector + node.label)
    if not node.is_leaf():
        child_prefix = prefix + ("    " if last else "│   ")
        for i, child in enumerate(node.children):
            print_tree(child, child_prefix, i == len(node.children) - 1)


def print_tree_result(node, prefix="", last=True):
    connector = "└── " if last else "├── "
    if node.pruned:
        line = f"{RED}{node.label}  [✂ pruned — never visited]{RESET}"
    else:
        val = f"  =  {GREEN}{node.result}{RESET}" if node.result is not None else ""
        line = node.label + val
    print(prefix + connector + line)
    if not node.is_leaf():
        child_prefix = prefix + ("    " if last else "│   ")
        for i, child in enumerate(node.children):
            print_tree_result(child, child_prefix, i == len(node.children) - 1)


def read_three_ints(prompt, color):
    while True:
        raw = input(f"{color}{prompt}{RESET} ").strip()
        parts = raw.split()
        if len(parts) == 3:
            try:
                return [int(x) for x in parts]
            except ValueError:
                pass
        print(f"{RED}  Please enter exactly 3 integers, e.g.:  3 12 8{RESET}")


def main():
    print(
        BOLD + "╔══════════════════════════════════════════╗\n"
        "║    Alpha-Beta Pruning  Visualization     ║\n"
        "╚══════════════════════════════════════════╝" + RESET
    )
    print()
    print(
        GRAY + "Tree structure:\n"
        "             A  [MAX]\n"
        "            /        \\\n"
        "        B [MIN]     C [MIN]\n"
        "        / | \\       / | \\\n"
        "       b1  b2  b3  c1  c2  c3" + RESET
    )
    print()

    b = read_three_ints("B scores  b1 b2 b3 >", YELLOW)
    c = read_three_ints("C scores  c1 c2 c3 >", MAGENTA)

    root = Node(
        "A [MAX]",
        children=[
            Node("B [MIN]", children=[Node(str(v), leaf_val=v) for v in b]),
            Node("C [MIN]", children=[Node(str(v), leaf_val=v) for v in c]),
        ],
    )

    print()
    print(BOLD + "── Input tree ────────────────────────────────────" + RESET)
    print_tree(root)
    print()

    print(f"{CYAN}Legend:{RESET}")
    print(f"{YELLOW}  α  = MAX player's best guaranteed score so far{RESET}")
    print(f"{MAGENTA}  β  = MIN player's best guaranteed score so far{RESET}")
    print(f"{GREEN}  ●  = visited / value returned{RESET}")
    print(f"{RED}  ✂  = pruned  (never visited){RESET}")
    print()

    print(BOLD + "── Search trace ──────────────────────────────────" + RESET)
    print()

    answer = search(root, is_max=True, alpha=float("-inf"), beta=float("inf"))

    print()
    print(BOLD + "── Final result ──────────────────────────────────" + RESET)
    print(f"Optimal value for MAX: {GREEN}{BOLD}{answer}{RESET}")
    print()

    print(BOLD + "── Tree with computed values ─────────────────────" + RESET)
    print_tree_result(root)


if __name__ == "__main__":
    main()
