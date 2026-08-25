export default function Terms() {
  return (
    <div className="max-w-3xl mx-auto py-12 px-6 font-sans text-zinc-300">
      <h1 className="text-2xl font-bold text-zinc-50 mb-4">Terms of Service</h1>
      <p className="text-xs text-zinc-500 mb-8">Last updated: {new Date().toLocaleDateString()}</p>
      
      <div className="space-y-6 text-sm leading-relaxed">
        <section>
          <h2 className="text-base font-semibold text-zinc-100 mb-2">1. Terms</h2>
          <p className="text-zinc-400 text-xs">
            By accessing LearnLens AI, you agree to be bound by these terms of service and all applicable laws and regulations.
          </p>
        </section>

        <section>
          <h2 className="text-base font-semibold text-zinc-100 mb-2">2. Use License</h2>
          <p className="text-zinc-400 text-xs">
            Permission is granted to temporarily access the materials (information or software) on LearnLens AI for personal, non-commercial educational use.
          </p>
        </section>

        <section>
          <h2 className="text-base font-semibold text-zinc-100 mb-2">3. Disclaimer</h2>
          <p className="text-zinc-400 text-xs">
            The materials on LearnLens AI are provided on an 'as is' basis without warranties of any kind.
          </p>
        </section>
      </div>
    </div>
  );
}
