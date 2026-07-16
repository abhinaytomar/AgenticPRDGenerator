import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";

interface MarkdownRendererProps {
  content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="markdown-content prose prose-violet dark:prose-invert max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
