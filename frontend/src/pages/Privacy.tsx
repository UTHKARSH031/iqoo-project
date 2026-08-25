export default function Privacy() {
  return (
    <div className="max-w-3xl mx-auto py-12 px-6 font-sans text-zinc-300">
      <h1 className="text-2xl font-bold text-zinc-50 mb-4">Privacy Policy</h1>
      <p className="text-xs text-zinc-500 mb-8">Last updated: {new Date().toLocaleDateString()}</p>
      
      <div className="space-y-6 text-sm leading-relaxed">
        <section>
          <h2 className="text-base font-semibold text-zinc-100 mb-2">1. Data Collection</h2>
          <p className="text-zinc-400 text-xs">
            We collect assessment performance data, topic accuracy scores, and session logs to generate adaptive practice recommendations.
          </p>
        </section>

        <section>
          <h2 className="text-base font-semibold text-zinc-100 mb-2">2. Data Usage</h2>
          <p className="text-zinc-400 text-xs">
            Your data is strictly utilized to compute topic mastery levels and provide aggregate analytics to course instructors.
          </p>
        </section>

        <section>
          <h2 className="text-base font-semibold text-zinc-100 mb-2">3. Security</h2>
          <p className="text-zinc-400 text-xs">
            We implement industry-standard encryption protocols to protect user credentials and performance records.
          </p>
        </section>
      </div>
    </div>
  );
}
