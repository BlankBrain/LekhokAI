import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border border-white/30 bg-glass/80 px-3 py-2 text-sm shadow-glass transition-colors placeholder:text-techno/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold focus-visible:border-gold disabled:cursor-not-allowed disabled:opacity-50 backdrop-blur-glass",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input } 