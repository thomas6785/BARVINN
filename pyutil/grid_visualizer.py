def display_grid(highlight_cell):
    """
    Display a 32x32 grid and highlight a specific cell.
    
    Args:
        highlight_cell: Integer between 1 and 1024 indicating which cell to highlight
    """
    if not (1 <= highlight_cell <= 1024):
        print(f"Error: Cell number must be between 1 and 1024, got {highlight_cell}")
        return
    
    # Convert 1-indexed cell number to 0-indexed row and column
    cell_idx = highlight_cell - 1
    highlight_row = cell_idx // 32
    highlight_col = cell_idx % 32
    
    # Print column headers
    print("    ", end="")
    for col in range(32):
        print(f"{col:2d} ", end="")
    print("\n    " + "---" * 32)
    
    # Print grid
    for row in range(32):
        print(f"{row:2d} |", end="")
        for col in range(32):
            if row == highlight_row and col == highlight_col:
                print(" ■ ", end="")  # Highlighted cell
            else:
                print(" □ ", end="")  # Empty cell
        print()
    
    print(f"\nHighlighted cell: {highlight_cell} (Row {highlight_row}, Col {highlight_col})")


if __name__ == "__main__":
    # Example usage
    display_grid(1)      # Top-left corner
    print("\n" + "="*100 + "\n")
    display_grid(513)    # Middle of grid
    print("\n" + "="*100 + "\n")
    display_grid(1024)   # Bottom-right corner
