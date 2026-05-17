import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function MarkdownRenderer({ content }) {
    return (
        <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
                h1: ({ node, ...props }) => (
                    <h1 className="text-2xl font-bold text-bob-text mb-4 mt-6 first:mt-0" {...props} />
                ),
                h2: ({ node, ...props }) => (
                    <h2 className="text-xl font-semibold text-bob-text mb-3 mt-6 first:mt-0" {...props} />
                ),
                h3: ({ node, ...props }) => (
                    <h3 className="text-lg font-semibold text-bob-primary mb-2 mt-4 first:mt-0" {...props} />
                ),
                h4: ({ node, ...props }) => (
                    <h4 className="text-base font-semibold text-bob-text mb-2 mt-3" {...props} />
                ),
                p: ({ node, ...props }) => (
                    <p className="text-sm text-bob-text/90 leading-relaxed mb-3" {...props} />
                ),
                ul: ({ node, ...props }) => (
                    <ul className="list-disc list-inside space-y-1.5 mb-3 text-sm text-bob-text/90 ml-2" {...props} />
                ),
                ol: ({ node, ...props }) => (
                    <ol className="list-decimal list-inside space-y-1.5 mb-3 text-sm text-bob-text/90 ml-2" {...props} />
                ),
                li: ({ node, ...props }) => (
                    <li className="text-sm text-bob-text/90 leading-relaxed" {...props} />
                ),
                code: ({ node, inline, ...props }) =>
                    inline ? (
                        <code className="bg-bob-surface px-1.5 py-0.5 rounded text-xs font-mono text-bob-accent" {...props} />
                    ) : (
                        <code className="block bg-bob-surface p-3 rounded-input text-xs font-mono text-bob-text overflow-x-auto mb-3" {...props} />
                    ),
                pre: ({ node, ...props }) => (
                    <pre className="bg-bob-surface p-3 rounded-input overflow-x-auto mb-3" {...props} />
                ),
                strong: ({ node, ...props }) => (
                    <strong className="font-semibold text-bob-text" {...props} />
                ),
                em: ({ node, ...props }) => (
                    <em className="italic text-bob-text/90" {...props} />
                ),
                a: ({ node, ...props }) => (
                    <a className="text-bob-primary hover:underline transition-all" {...props} />
                ),
                blockquote: ({ node, ...props }) => (
                    <blockquote className="border-l-4 border-bob-primary pl-4 py-2 mb-3 text-sm text-bob-muted italic" {...props} />
                ),
                hr: ({ node, ...props }) => (
                    <hr className="border-bob-muted/30 my-6" {...props} />
                ),
                table: ({ node, ...props }) => (
                    <div className="overflow-x-auto mb-3">
                        <table className="min-w-full text-sm border border-bob-muted/20" {...props} />
                    </div>
                ),
                th: ({ node, ...props }) => (
                    <th className="border border-bob-muted/20 px-3 py-2 bg-bob-surface text-left font-semibold text-bob-text" {...props} />
                ),
                td: ({ node, ...props }) => (
                    <td className="border border-bob-muted/20 px-3 py-2 text-bob-text/90" {...props} />
                ),
            }}
        >
            {content}
        </ReactMarkdown>
    )
}