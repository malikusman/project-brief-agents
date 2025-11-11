import type { BriefPayload } from '../types/brief'

interface BriefPreviewProps {
  payload: BriefPayload
}

export function BriefPreview({ payload }: BriefPreviewProps) {
  const { summary, brief, follow_up_questions } = payload

  return (
    <div className="brief-preview">
      <header>
        <h2>{brief.project_title}</h2>
        <p>{brief.project_description}</p>
      </header>

      <section>
        <h3>Purpose</h3>
        <p>{brief.purpose}</p>
      </section>

      <section className="grid">
        <div>
          <h4>Expected Outcomes</h4>
          <ul>
            {brief.expected_outcomes.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Business Model</h4>
          <ul>
            {brief.business_model.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Success Metrics</h4>
          <ul>
            {brief.success_metrics.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="grid">
        <div>
          <h4>Constraints & Risks</h4>
          <ul>
            {brief.constraints.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Timeline</h4>
          <p>{brief.timeline}</p>
        </div>
        <div>
          <h4>Target Users</h4>
          <ul>
            {brief.target_users.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="grid">
        <div>
          <h4>Opportunities</h4>
          <ul>
            {brief.opportunity_areas.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Suggested Reads</h4>
          <ul>
            {brief.suggested_reads.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Ideas Board</h4>
          <ul>
            {brief.ideas_board.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section>
        <h3>Follow-up Questions</h3>
        {follow_up_questions.length ? (
          <ul>
            {follow_up_questions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p>All key areas covered. Feel free to iterate further.</p>
        )}
      </section>

      <section>
        <h3>Summary Highlights</h3>
        <dl>
          <dt>Problem</dt>
          <dd>{summary.problem || 'Pending capture.'}</dd>
          <dt>Solution</dt>
          <dd>{summary.solution || 'Pending capture.'}</dd>
        </dl>
      </section>
    </div>
  )
}
