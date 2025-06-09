import * as React from "react"
import { cn } from "@/lib/utils"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[60px] w-full rounded-lg border border-white/30 bg-glass/80 px-3 py-2 text-sm shadow-glass transition-colors placeholder:text-techno/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold focus-visible:border-gold disabled:cursor-not-allowed disabled:opacity-50 font-mono backdrop-blur-glass",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea } 