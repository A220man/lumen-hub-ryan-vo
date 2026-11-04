/** SMS Template Form Component */

import { useState, useEffect } from "react";
import { validateTemplate, previewTemplate, type SMSTemplate, type SMSTemplateCreate, type SMSTemplateUpdate, type SMSTemplateValidation, type SMSTemplatePreview } from "../../services/smsTemplates";

interface SMSTemplateFormProps {
  initialData: SMSTemplate | null;
  onSave: (data: SMSTemplateCreate | SMSTemplateUpdate) => Promise<void>;
  onCancel: () => void;
  onValidate: (validation: SMSTemplateValidation) => void;
  onPreview: (preview: SMSTemplatePreview) => void;
}

export function SMSTemplateForm({ initialData, onSave, onCancel, onValidate, onPreview }: SMSTemplateFormProps) {
  const isEditing = !!initialData;
  const [name, setName] = useState(initialData?.name || "");
  const [content, setContent] = useState(initialData?.content || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [validating, setValidating] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [validation, setValidation] = useState<SMSTemplateValidation | null>(null);
  const [preview, setPreview] = useState<SMSTemplatePreview | null>(null);
  const [previewVariables, setPreviewVariables] = useState<Record<string, string>>({});

  // Extract variables from content
  const variableMatches = content.matchAll(/{{?(\w+)}?}/g);
  const variables = Array.from(variableMatches).map((m: RegExpMatchArray) => m[1]);
  const uniqueVariables = [...new Set(variables)].filter(v => v !== "otp");

  useEffect(() => {
    if (initialData) {
      setName(initialData.name);
      setContent(initialData.content);
      setDescription(initialData.description || "");
      // Initialize preview variables
      const vars: Record<string, string> = {};
      uniqueVariables.forEach(v => vars[v] = "");
      vars.otp = "123456";
      setPreviewVariables(vars);
    }
  }, [initialData]);

  const handleValidate = async () => {
    setValidating(true);
    try {
      const data: SMSTemplateCreate = { name: name || "temp", content, description };
      const result = await validateTemplate(data);
      setValidation(result);
      onValidate(result);
    } catch (err) {
      console.error("Validation failed:", err);
    } finally {
      setValidating(false);
    }
  };

  const handlePreview = async () => {
    setPreviewing(true);
    try {
      const result = await previewTemplate({ content, variables: previewVariables });
      setPreview(result);
      onPreview(result);
    } catch (err) {
      console.error("Preview failed:", err);
    } finally {
      setPreviewing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const data = isEditing
      ? { content, description } as SMSTemplateUpdate
      : { name, content, description } as SMSTemplateCreate;
    await onSave(data);
  };

  const handleVariableChange = (key: string, value: string) => {
    setPreviewVariables(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="sms-template-form">
      <form onSubmit={handleSubmit}>
        {!isEditing && (
          <div className="form-field">
            <label htmlFor="name">Template Name *</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={100}
              disabled={isEditing}
            />
            <small>Unique identifier for the template</small>
          </div>
        )}

        <div className="form-field">
          <label htmlFor="content">Template Content *</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            maxLength={1600}
            rows={6}
            placeholder="Enter your SMS template. Use {otp} or {{otp}} for the OTP placeholder.\nExample: Your verification code is: {otp}"
          />
          <small>
            {content.length}/1600 characters. 
            {validation?.warnings.map((w: string, i: number) => <span key={i} className="warning"> ⚠ {w}</span>)}
          </small>
        </div>

        <div className="form-field">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={500}
            rows={2}
            placeholder="Optional description"
          />
        </div>

        {/* Validation Status */}
        {validation && (
          <div className={`validation-status ${validation.valid ? "valid" : "invalid"}`}>
            <h4>Validation Result</h4>
            <p className={validation.valid ? "success" : "error"}>
              {validation.valid ? "✓ Template is valid" : "✗ Template has errors"}
            </p>
            {validation.errors.length > 0 && (
              <ul className="errors">
                {validation.errors.map((err: string, i: number) => <li key={i}>{err}</li>)}
              </ul>
            )}
            {validation.warnings.length > 0 && (
              <ul className="warnings">
                {validation.warnings.map((warn: string, i: number) => <li key={i}>⚠ {warn}</li>)}
              </ul>
            )}
            <p>
              WebOTP Compatible: <strong>{validation.is_webotp_compatible ? "Yes" : "No"}</strong>
            </p>
          </div>
        )}

        {/* Preview Section */}
        {preview && (
          <div className="preview-section">
            <h4>Preview</h4>
            <div className="preview-variables">
              <label>
                OTP: <input type="text" value={previewVariables.otp || ""} onChange={(e) => handleVariableChange("otp", e.target.value)} />
              </label>
              {uniqueVariables.map(v => (
                <label key={v}>
                  {v}: <input type="text" value={previewVariables[v] || ""} onChange={(e) => handleVariableChange(v, e.target.value)} />
                </label>
              ))}
            </div>
            <div className="preview-output">
              <pre>{preview.rendered}</pre>
              <p>
                Characters: {preview.character_count} | Segments: {preview.segment_count}
                {preview.is_webotp_compatible && <span className="webotp-badge">WebOTP ✓</span>}
              </p>
            </div>
          </div>
        )}

        <div className="form-actions">
          <button type="button" onClick={handleValidate} disabled={validating}>
            {validating ? "Validating..." : "Validate"}
          </button>
          <button type="button" onClick={handlePreview} disabled={previewing}>
            {previewing ? "Previewing..." : "Preview"}
          </button>
          <button type="submit" className="primary">
            {isEditing ? "Update" : "Create"}
          </button>
          <button type="button" onClick={onCancel} className="secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
