import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 px-4 py-2 backdrop-blur-glass border border-white/30 shadow-glass bg-glass/80 hover:bg-gold hover:text-white",
  {
    variants: {
      variant: {
        default: "bg-techno text-white hover:bg-gold hover:text-white",
        gold: "bg-gold text-white hover:bg-techno hover:text-gold",
        outline: "bg-glass/60 text-techno border border-gold hover:bg-gold/20 hover:text-gold",
        secondary: "bg-white/80 text-techno border border-techno hover:bg-gold/20 hover:text-gold",
        destructive: "bg-red-500 text-white hover:bg-red-600",
        ghost: "bg-transparent hover:bg-gold/10 text-techno",
        link: "underline-offset-4 hover:underline text-gold",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3",
        lg: "h-12 px-6 text-lg",
        icon: "h-10 w-10 p-0",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };

// FavouriteButton: star icon, filled if favourited, outline if not
type FavouriteButtonProps = {
  isFavourited: boolean;
  onClick: () => void;
  className?: string;
  size?: number;
  disabled?: boolean;
};

export function FavouriteButton({ isFavourited, onClick, className, size = 24, disabled }: FavouriteButtonProps) {
  return (
    <button
      type="button"
      aria-label={isFavourited ? "Unfavourite" : "Favourite"}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "transition-colors p-1 rounded-full hover:bg-gold/20 focus:outline-none focus:ring-2 focus:ring-gold",
        className
      )}
    >
      {isFavourited ? (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="#FFD700" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      ) : (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#FFD700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      )}
    </button>
  );
} 