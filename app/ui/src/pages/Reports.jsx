import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/index';
import { Button } from '../components/ui/Button';
import { apiClient, API_BASE_URL } from '../services/apiClient';
import { FileText, Download, ExternalLink, AlertTriangle, FileSpreadsheet } from 'lucide-react';

export const Reports = () => {
  const [reports, setReports] = useState({});
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const res = await apiClient.getReports();
        setReports(res || {});
      } catch (err) {
        setErrorMsg("Failed to load reports metadata.");
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  const handleDownload = (filename) => {
    window.open(`${API_BASE_URL}/report-content?file=${filename}`, '_blank');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1200, paddingBottom: 'var(--space-8)' }}>
      <div className="page-header">
        <h1 className="page-title">Project Reports & Artifacts</h1>
        <p className="page-subtitle">Access genuine project-generated research reports, validation data, and exported tables.</p>
      </div>

      {errorMsg && (
        <div style={{ padding: 'var(--space-3)', background: 'rgba(220, 38, 38, 0.1)', color: 'var(--accent-danger)', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <AlertTriangle size={16} /> {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>Loading report registry...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
          {Object.entries(reports).map(([category, items]) => (
            <div key={category}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
                {category}
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 'var(--space-4)' }}>
                {items.map((item, idx) => (
                  <Card key={idx} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {item.type === 'csv' ? <FileSpreadsheet size={18} style={{color: 'var(--accent-success)'}}/> : <FileText size={18} style={{color: 'var(--accent-primary)'}}/>}
                        <h3 style={{ fontSize: 'var(--fs-base)', fontWeight: 600, margin: 0 }}>{item.title}</h3>
                      </div>
                      <Badge variant={item.type === 'csv' ? 'success' : 'primary'}>{item.type.toUpperCase()}</Badge>
                    </div>
                    
                    <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', marginBottom: '1.5rem', flex: 1 }}>
                      {item.desc}
                    </p>
                    
                    <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', fontFamily: 'var(--font-mono, monospace)', marginBottom: '1rem' }}>
                      {item.file}
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <Button variant="outline" size="sm" onClick={() => handleDownload(item.file)} style={{ flex: 1, justifyContent: 'center' }}>
                        <ExternalLink size={14} /> Open
                      </Button>
                      <Button variant="secondary" size="sm" onClick={() => handleDownload(item.file)} style={{ flex: 1, justifyContent: 'center' }}>
                        <Download size={14} /> Download
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
