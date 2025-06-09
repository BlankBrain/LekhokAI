interface ImageDisplayProps {
  prompt: string;
}

export default function ImageDisplay({ prompt }: ImageDisplayProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-gray-50 p-4">
        <h3 className="text-sm font-medium text-gray-900">Image Prompt</h3>
        <div className="mt-2 text-sm text-gray-700">
          <pre className="whitespace-pre-wrap">{prompt}</pre>
        </div>
      </div>
      <div className="rounded-lg border-2 border-dashed border-gray-300 p-4 text-center">
        <p className="text-sm text-gray-500">Generated image will appear here</p>
      </div>
    </div>
  );
} 