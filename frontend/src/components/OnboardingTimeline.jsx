export default function OnboardingTimeline({ steps }) {
    if (!steps || steps.length === 0) {
        return null
    }

    return (
        <div className="space-y-6">
            {steps.map((step, index) => (
                <div key={index} className="flex gap-4">
                    <div className="flex flex-col items-center">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-bob-primary text-white font-mono font-semibold shadow-lg">
                            {index + 1}
                        </div>
                        {index < steps.length - 1 && (
                            <div className="w-0.5 flex-1 bg-bob-muted/30 mt-2 min-h-[40px]" />
                        )}
                    </div>
                    <div className="flex-1 pb-8">
                        <h3 className="font-semibold text-bob-text mb-2">{step.title}</h3>
                        {step.description && (
                            <p className="text-sm text-bob-muted leading-relaxed whitespace-pre-wrap">
                                {step.description}
                            </p>
                        )}
                    </div>
                </div>
            ))}
        </div>
    )
}

// Made with Bob
