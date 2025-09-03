import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import VariantCard from "./VariantCard";

const mockVariant = {
  id: "test-variant-1",
  text: "This is a test variant for LinkedIn",
  length: 150,
  readability: "Good",
  tone: "professional",
};

describe("VariantCard", () => {
  const defaultProps = {
    variant: mockVariant,
    channel: "linkedin",
    onEdit: vi.fn(),
    onAccept: vi.fn(),
    onCopy: vi.fn(),
    onDownload: vi.fn(),
    onToggleFavorite: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("renders variant information correctly", () => {
    render(<VariantCard {...defaultProps} />);

    expect(screen.getByText("linkedin")).toBeInTheDocument();
    expect(screen.getByText("150 chars")).toBeInTheDocument();
    expect(screen.getByText("Good")).toBeInTheDocument();
    expect(
      screen.getByText("This is a test variant for LinkedIn")
    ).toBeInTheDocument();
  });

  test("calls onEdit when edit button is clicked", () => {
    render(<VariantCard {...defaultProps} />);

    const editButton = screen.getByText("Edit");
    fireEvent.click(editButton);

    expect(defaultProps.onEdit).toHaveBeenCalledWith(mockVariant);
  });

  test("calls onAccept when accept button is clicked", () => {
    render(<VariantCard {...defaultProps} />);

    const acceptButton = screen.getByText("Accept");
    fireEvent.click(acceptButton);

    expect(defaultProps.onAccept).toHaveBeenCalledWith(mockVariant.id);
  });

  test("toggles favorite state when heart button is clicked", () => {
    render(<VariantCard {...defaultProps} />);

    // Find the heart button by its class (it's the first button with the heart styling)
    const buttons = screen.getAllByRole("button");
    const heartButton = buttons.find(button =>
      button.className.includes("hover:text-red-400")
    );

    expect(heartButton).toBeDefined();
    fireEvent.click(heartButton);

    expect(defaultProps.onToggleFavorite).toHaveBeenCalledWith(
      mockVariant.id,
      true
    );
  });

  test("shows correct readability color for different levels", () => {
    const { rerender } = render(
      <VariantCard
        {...defaultProps}
        variant={{ ...mockVariant, readability: "Excellent" }}
      />
    );
    expect(screen.getByText("Excellent")).toHaveClass("text-green-400");

    rerender(
      <VariantCard
        {...defaultProps}
        variant={{ ...mockVariant, readability: "Poor" }}
      />
    );
    expect(screen.getByText("Poor")).toHaveClass("text-red-400");
  });
});
