export default function DependencyGraph({ moduleName, importingFiles }) {
    if (!importingFiles || importingFiles.length === 0) {
        return null
    }

    const centerX = 200
    const centerY = 150
    const radius = 100
    const filesToShow = importingFiles.slice(0, 8) // Show max 8 files

    return (
        <div className="my-6 overflow-x-auto">
            <svg
                width="400"
                height="300"
                className="mx-auto"
                viewBox="0 0 400 300"
            >
                {/* Connecting lines */}
                {filesToShow.map((file, i) => {
                    const angle = (i * 2 * Math.PI) / filesToShow.length - Math.PI / 2
                    const x = centerX + radius * Math.cos(angle)
                    const y = centerY + radius * Math.sin(angle)

                    return (
                        <line
                            key={`line-${i}`}
                            x1={centerX}
                            y1={centerY}
                            x2={x}
                            y2={y}
                            stroke="#8D8D8D"
                            strokeWidth="2"
                            strokeDasharray="4,4"
                            opacity="0.5"
                        />
                    )
                })}

                {/* Importing file nodes */}
                {filesToShow.map((file, i) => {
                    const angle = (i * 2 * Math.PI) / filesToShow.length - Math.PI / 2
                    const x = centerX + radius * Math.cos(angle)
                    const y = centerY + radius * Math.sin(angle)
                    const fileName = file.split('/').pop()
                    const displayName = fileName.length > 12 ? fileName.slice(0, 10) + '...' : fileName

                    return (
                        <g key={`node-${i}`}>
                            <circle
                                cx={x}
                                cy={y}
                                r="25"
                                fill="#24A148"
                                stroke="#F4F4F4"
                                strokeWidth="2"
                            />
                            <text
                                x={x}
                                y={y}
                                textAnchor="middle"
                                dominantBaseline="middle"
                                fill="white"
                                fontSize="10"
                                fontWeight="600"
                                className="font-mono"
                            >
                                <title>{file}</title>
                                {displayName}
                            </text>
                        </g>
                    )
                })}

                {/* Center module node */}
                <circle
                    cx={centerX}
                    cy={centerY}
                    r="35"
                    fill="#0043CE"
                    stroke="#F4F4F4"
                    strokeWidth="3"
                />
                <text
                    x={centerX}
                    y={centerY}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="white"
                    fontSize="12"
                    fontWeight="700"
                    className="font-mono"
                >
                    {moduleName.length > 10 ? moduleName.slice(0, 8) + '...' : moduleName}
                </text>

                {/* Legend */}
                <text
                    x="10"
                    y="20"
                    fill="#8D8D8D"
                    fontSize="10"
                    className="font-mono"
                >
                    {importingFiles.length} file{importingFiles.length !== 1 ? 's' : ''} import this module
                </text>

                {importingFiles.length > 8 && (
                    <text
                        x="10"
                        y="35"
                        fill="#F1C21B"
                        fontSize="9"
                        className="font-mono"
                    >
                        Showing first 8 of {importingFiles.length}
                    </text>
                )}
            </svg>
        </div>
    )
}

// Made with Bob
