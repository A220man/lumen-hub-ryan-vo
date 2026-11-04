/** SMS Template List Component */

import { useState, useEffect } from "react";
import { listTemplates, deleteTemplate, type SMSTemplate } from "../../services/smsTemplates";

interface SMSTemplateListProps {
  onEdit: (template: SMSTemplate) => void;
  onPreview: (template: SMSTemplate) => void;
}

export function SMSTemplateList({ onEdit, onPreview }: SMSTemplateListProps) {
  const [templates, setTemplates] = useState<SMSTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listTemplates();
      setTemplates(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load templates");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleDelete = async (name: string) => {
    if (!window.confirm(`Delete template "${name}"?`)) return;
    try {
      await deleteTemplate(name);
      fetchTemplates();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete template");
    }
  };

  if (loading) {
    return <div className="sms-template-list loading">Loading templates...</div>;
  }

  if (error) {
    return <div className="sms-template-list error">Error: {error}</div>;
  }

  return (
    <div className="sms-template-list">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Created</th>
            <th>Updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {templates.map((template) => (
            <tr key={template.name}>
              <td>{template.name}</td>
              <td>{template.description || "-"}</td>
              <td>{new Date(template.created_at).toLocaleString()}</td>
              <td>{new Date(template.updated_at).toLocaleString()}</td>
              <td>
                <button onClick={() => onEdit(template)}>Edit</button>
                <button onClick={() => onPreview(template)}>Preview</button>
                <button onClick={() => handleDelete(template.name)} className="danger">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {templates.length === 0 && (
        <p className="empty">No templates yet. Click "New Template" to create one.</p>
      )}
    </div>
  );
}
