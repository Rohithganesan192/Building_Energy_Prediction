import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, GlassPanel } from '../components/ui/Card';
import { Badge } from '../components/ui/index';
import { Button } from '../components/ui/Button';
import { apiClient } from '../services/apiClient';
import { Search, MapPin, Box, Square, ArrowRight, Building2, AlertTriangle, Layers } from 'lucide-react';

export const Buildings = () => {
  const navigate = useNavigate();
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [siteFilter, setSiteFilter] = useState('');
  const [useFilter, setUseFilter] = useState('');
  const [selectedBuilding, setSelectedBuilding] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await apiClient.getBuildings();
        setBuildings(res.buildings || []);
      } catch (err) {
        setErrorMsg("Failed to load building metadata.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const sites = useMemo(() => [...new Set(buildings.map(b => b.site_id))].sort((a,b)=>a-b), [buildings]);
  const primaryUses = useMemo(() => [...new Set(buildings.map(b => b.primary_use))].sort(), [buildings]);

  const filteredBuildings = useMemo(() => {
    return buildings.filter(b => {
      const matchSearch = b.building_id.toString().includes(searchQuery);
      const matchSite = siteFilter === '' || b.site_id.toString() === siteFilter;
      const matchUse = useFilter === '' || b.primary_use === useFilter;
      return matchSearch && matchSite && matchUse;
    });
  }, [buildings, searchQuery, siteFilter, useFilter]);

  const handleUseForPrediction = (b) => {
    // In a full implementation we'd pass building data to populate the Predict page context.
    // For this app we use navigation state.
    navigate('/predict', { state: { building: b } });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1200, paddingBottom: 'var(--space-8)' }}>
      <div className="page-header">
        <h1 className="page-title">Building Explorer</h1>
        <p className="page-subtitle">Search and filter the ASHRAE building dataset metadata.</p>
      </div>

      {errorMsg && (
        <div style={{ padding: 'var(--space-3)', background: 'rgba(220, 38, 38, 0.1)', color: 'var(--accent-danger)', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <AlertTriangle size={16} /> {errorMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 3fr', gap: 'var(--space-6)' }}>
        
        {/* Sidebar Filters */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <Card title="Search & Filter">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginTop: '1rem' }}>
              <div>
                <label style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-secondary)', fontWeight: 600 }}>Building ID</label>
                <div style={{ position: 'relative', marginTop: '0.25rem' }}>
                  <Search size={14} style={{ position: 'absolute', top: '50%', left: 10, transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input 
                    type="text" 
                    className="input" 
                    placeholder="Search by ID..." 
                    style={{ paddingLeft: '2rem' }}
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-secondary)', fontWeight: 600 }}>Site ID</label>
                <select className="input" style={{ marginTop: '0.25rem' }} value={siteFilter} onChange={e => setSiteFilter(e.target.value)}>
                  <option value="">All Sites</option>
                  {sites.map(s => <option key={s} value={s}>Site {s}</option>)}
                </select>
              </div>
              <div>
                <label style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-secondary)', fontWeight: 600 }}>Primary Use</label>
                <select className="input" style={{ marginTop: '0.25rem' }} value={useFilter} onChange={e => setUseFilter(e.target.value)}>
                  <option value="">All Uses</option>
                  {primaryUses.map(u => <option key={u} value={u}>{u}</option>)}
                </select>
              </div>
            </div>
          </Card>
        </div>

        {/* Main Content */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          
          {selectedBuilding && (
            <GlassPanel style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Building2 size={24} style={{ color: 'var(--accent-primary)' }} />
                    Building {selectedBuilding.building_id}
                  </h2>
                  <Badge variant="neutral">{selectedBuilding.primary_use}</Badge>
                </div>
                <Button variant="primary" onClick={() => handleUseForPrediction(selectedBuilding)}>
                  Use for Prediction <ArrowRight size={14} />
                </Button>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-subtle)' }}>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><MapPin size={12}/> Site ID</div>
                  <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>{selectedBuilding.site_id}</div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Square size={12}/> Square Feet</div>
                  <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>{selectedBuilding.square_feet?.toLocaleString() || 'Unknown'}</div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Box size={12}/> Year Built</div>
                  <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>
                    {selectedBuilding.year_built ? selectedBuilding.year_built : <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Missing metadata</span>}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Layers size={12}/> Floor Count</div>
                  <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 500, color: 'var(--text-secondary)' }}>
                    {selectedBuilding.floor_count ? selectedBuilding.floor_count : <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Missing metadata</span>}
                  </div>
                </div>
              </div>
            </GlassPanel>
          )}

          <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
            <div style={{ padding: '1rem', background: 'var(--surface-secondary)', borderBottom: '1px solid var(--border-subtle)', fontSize: 'var(--fs-sm)', fontWeight: 600, color: 'var(--text-secondary)' }}>
              {loading ? 'Loading buildings...' : `${filteredBuildings.length} Buildings Found`}
            </div>
            
            <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
              {filteredBuildings.map(b => (
                <div 
                  key={b.building_id}
                  onClick={() => setSelectedBuilding(b)}
                  style={{ 
                    padding: '1rem', 
                    borderBottom: '1px solid var(--border-subtle)', 
                    display: 'grid', 
                    gridTemplateColumns: '80px 100px 1fr 120px', 
                    alignItems: 'center',
                    gap: '1rem',
                    cursor: 'pointer',
                    background: selectedBuilding?.building_id === b.building_id ? 'var(--surface-secondary)' : 'transparent',
                  }}
                  onMouseEnter={(e) => { if (selectedBuilding?.building_id !== b.building_id) e.currentTarget.style.background = 'rgba(6,182,212,0.03)' }}
                  onMouseLeave={(e) => { if (selectedBuilding?.building_id !== b.building_id) e.currentTarget.style.background = 'transparent' }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>ID {b.building_id}</div>
                  <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)' }}>Site {b.site_id}</div>
                  <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>{b.primary_use}</div>
                  <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', textAlign: 'right' }}>{b.square_feet?.toLocaleString()} sqft</div>
                </div>
              ))}
              {!loading && filteredBuildings.length === 0 && (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No buildings match the current filters.</div>
              )}
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};
