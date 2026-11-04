/** SMS Templates Page */

import { useState } from "react";
import { createTemplate, updateTemplate, type SMSTemplate } from "../services/smsTemplates";
import { SMSTemplateList } from "../components/smsTemplates/SMSTemplateList";
import { SMSTemplateForm } from "../components/smsTemplates/SMSTemplateForm";
import { type SMSTemplateValidation, type SMSTemplatePreview } from "../types";

export function SMSTemplatesPage() {
  const [editingTemplate, setEditingTemplate] = useState<SMSTemplate | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [validation, setValidation] = useState<SMSTemplateValidation | null>(null);
  const [preview, setPreview] = useState<SMSTemplatePreview | null>(null);

  const handleNewTemplate = () => {
    setEditingTemplate(null);
    setShowForm(true);
    setValidation(null);
    setPreview(null);
  };

  const handleEdit = (template: SMSTemplate) => {
    setEditingTemplate(template);
    setShowForm(true);
    setValidation(null);
    setPreview(null);
  };

  const handlePreview = (template: SMSTemplate) => {
    // Preview is handled in the form, so we open form in preview mode
    setEditingTemplate(template);
    setShowForm(true);
  };

  const handleSave = async (data: any) => {
    try {
      if (editingTemplate) {
        await updateTemplate(editingTemplate.name, data);
      } else {
        await createTemplate(data as any);
      }
      setShowForm(false);
      setEditingTemplate(null);
      // Trigger refresh by updating a key or using a callback
      window.location.reload();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save template");
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTemplate(null);
    setValidation(null);
    setPreview(null);
  };

  return (
    <div className="sms-templates-page">
      <div className="page-header">
        <h1>SMS OTP Templates</h1>
        <button onClick={handleNewTemplate} className="primary">New Template</button>
      </div>

      {showForm ? (
        <SMSTemplateForm
          initialData={editingTemplate}
          onSave={handleSave}
          onCancel={handleCancel}
          onValidate={setValidation}
          onPreview={setPreview}
        />
      ) : (
        <SMSTemplateList onEdit={handleEdit} onPreview={handlePreview} />
      )}
    </div>
  );
}
