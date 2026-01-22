import { Card, ConfigPreview } from "ui";
import type { ValidationConfig } from "../app/config/types";
import "../styles/review-step.css";

interface ReviewStepProps {
  config: ValidationConfig;
  normalizeConfig: (config: ValidationConfig) => ValidationConfig;
}

export function ReviewStep({ config, normalizeConfig }: ReviewStepProps) {
  return (
    <div className="review-container">
      <Card title="Configuration Preview" helperText="Review and download your configuration file">
        <ConfigPreview config={normalizeConfig(config)} />
      </Card>
    </div>
  );
}
