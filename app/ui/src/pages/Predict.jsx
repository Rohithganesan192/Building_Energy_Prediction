import React, { useState } from 'react';
import { Card, GlassPanel } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge, StatusBadge } from '../components/ui/index';
import { apiClient } from '../services/apiClient';
import { usePrediction } from '../store/PredictionContext';
import { useNavigate } from 'react-router-dom';
import { Zap, AlertTriangle, Building2, Clock, CloudRain, Database, ArrowRight } from 'lucide-react';

const DEMO_ROW = {
  building_id: 565,
  meter: 0,
  timestamp: "2016-01-08 00:00:00",
  actual_reading: 8.25,
  hour: 0,
  day_of_week: 4,
  month: 1,
  day_of_year: 8,
  is_weekend: 0,
  site_id: 4,
  primary_use: "Education",
  square_feet: 15326,
  year_built: 1954,
  floor_count: 2,
  air_temperature: 12.2,
  cloud_coverage: 4.0,
  dew_temperature: 7.2,
  precip_depth_1_hr: 0.0,
  sea_level_pressure: 1015.2,
  wind_direction: 300.0,
  wind_speed: 3.6,
  lag_1: 7.75,
  lag_24: 8.25,
  lag_168: 7.25,
  rolling_mean_24: 13.114583333333334,
  rolling_std_24: 5.636632496961028,
  rolling_mean_168: 10.60625,
  rolling_std_168: 4.392829580299798
};

const PRIMARY_USES = [
  "Education", "Office", "Entertainment/public assembly", "Lodging/residential",
  "Public services", "Healthcare", "Other", "Parking", "Warehouse/storage",
  "Manufacturing/industrial", "Retail", "Services", "Technology/science", "Food sales and service", "Utility"
];

const METER_OPTIONS = [
  { value: 0, label: "0 — Electricity" },
  { value: 1, label: "1 — Chilled Water" },
  { value: 2, label: "2 — Steam" },
  { value: 3, label: "3 — Hot Water" }
];

const FormGroup = ({ label, children, required = true }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
    <label style={{ fontSize: 'var(--fs-xs)', fontWeight: 600, color: 'var(--text-secondary)' }}>
      {label} {required && <span style={{ color: 'var(--accent-danger)' }}>*</span>}
    </label>
    {children}
  </div>
);

export const Predict = () => {
  const [mode, setMode] = useState('demo'); // 'demo' or 'manual'
  
  const [formData, setFormData] = useState({
    site_id: '', primary_use: 'Education', square_feet: '', year_built: '', floor_count: '', meter: 0,
    hour: '', day_of_week: '', month: '', day_of_year: '', is_weekend: 0,
    air_temperature: '', cloud_coverage: '', dew_temperature: '', precip_depth_1_hr: '', sea_level_pressure: '', wind_direction: '', wind_speed: '',
    lag_1: '', lag_24: '', lag_168: '', rolling_mean_24: '', rolling_mean_168: '', rolling_std_24: '', rolling_std_168: ''
  });

  const { setCurrentFeatures, setPredictionResult } = usePrediction();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const calculateCyclic = (hour, dayOfWeek, month) => {
    const h = parseFloat(hour) || 0;
    const d = parseFloat(dayOfWeek) || 0;
    const m = parseFloat(month) || 0;
    return {
      hour_sin: Math.sin(2 * Math.PI * h / 24), hour_cos: Math.cos(2 * Math.PI * h / 24),
      day_of_week_sin: Math.sin(2 * Math.PI * d / 7), day_of_week_cos: Math.cos(2 * Math.PI * d / 7),
      month_sin: Math.sin(2 * Math.PI * m / 12), month_cos: Math.cos(2 * Math.PI * m / 12),
    };
  };

  const handlePredictDemo = async () => {
    setLoading(true);
    setErrorMsg(null);
    setResult(null);

    const cyclic = calculateCyclic(DEMO_ROW.hour, DEMO_ROW.day_of_week, DEMO_ROW.month);
    const payload = { ...DEMO_ROW, ...cyclic };
    delete payload.building_id;
    delete payload.timestamp;
    delete payload.actual_reading;

    try {
      const response = await apiClient.predict(payload);
      if (response.status === "insufficient_history") {
        setErrorMsg("Historical data required for this model is unavailable for this observation.");
      } else if (response.status === "success") {
        setResult({ ...response, is_demo: true, actual_reading: DEMO_ROW.actual_reading });
        setCurrentFeatures(payload);
        setPredictionResult(response);
      } else {
        setErrorMsg("An error occurred while generating the prediction.");
      }
    } catch (err) {
      setErrorMsg("A technical error occurred while connecting to the prediction service.");
    } finally {
      setLoading(false);
    }
  };

  const handlePredictManual = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setResult(null);

    const parsedData = { ...formData };
    let hasEmptyRequired = false;
    
    Object.keys(parsedData).forEach(key => {
      if (key !== 'primary_use') {
        if (parsedData[key] === '' || parsedData[key] === null) {
            hasEmptyRequired = true;
        }
        parsedData[key] = parseFloat(parsedData[key]);
      }
    });

    if (hasEmptyRequired) {
        setErrorMsg("All fields are required. Please fill out the entire form.");
        setLoading(false);
        return;
    }

    const cyclic = calculateCyclic(parsedData.hour, parsedData.day_of_week, parsedData.month);
    const payload = { ...parsedData, ...cyclic };

    try {
      const response = await apiClient.predict(payload);
      if (response.status === "insufficient_history") {
        setErrorMsg("Historical data required for this model is unavailable for this observation.");
      } else if (response.status === "success") {
        setResult(response);
        setCurrentFeatures(payload);
        setPredictionResult(response);
      } else {
        setErrorMsg("An error occurred while generating the prediction.");
      }
    } catch (err) {
      setErrorMsg("A technical error occurred while connecting to the prediction service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: 1200, paddingBottom: 'var(--space-8)' }}>
      
      <div className="page-header">
        <h1 className="page-title">Energy Prediction</h1>
        <p className="page-subtitle">Generate an explainable building energy consumption prediction.</p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <Button variant={mode === 'demo' ? 'primary' : 'outline'} onClick={() => { setMode('demo'); setResult(null); setErrorMsg(null); }}>
          Real ASHRAE Observation (Default)
        </Button>
        <Button variant={mode === 'manual' ? 'primary' : 'outline'} onClick={() => { setMode('manual'); setResult(null); setErrorMsg(null); }}>
          Advanced Manual Input (Testing)
        </Button>
      </div>
      <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', marginBottom: 'var(--space-2)' }}>
        Select a verified ASHRAE observation for the normal workflow. Advanced manual input is provided only for testing and experimentation.
      </p>

      {mode === 'demo' && (
        <Card title="Genuine Observation Selected" action={<Badge variant="success">ASHRAE Validated</Badge>}>
          <div style={{ padding: 'var(--space-4)' }}>
            <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
              Using verified genuine observation from the ASHRAE Great Energy Predictor III dataset.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', background: 'var(--surface-secondary)', padding: 'var(--space-4)', borderRadius: 'var(--radius-sm)' }}>
              <div><strong style={{color:'var(--text-primary)'}}>Building ID:</strong> 565</div>
              <div><strong style={{color:'var(--text-primary)'}}>Site ID:</strong> 4</div>
              <div><strong style={{color:'var(--text-primary)'}}>Timestamp:</strong> 2016-01-08 00:00:00</div>
              <div><strong style={{color:'var(--text-primary)'}}>Primary Use:</strong> Education</div>
              <div><strong style={{color:'var(--text-primary)'}}>Meter:</strong> Electricity</div>
            </div>
            
            <div style={{ marginTop: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
              <Button variant="primary" onClick={handlePredictDemo} disabled={loading}>
                {loading ? 'Generating...' : 'Generate Prediction'}
              </Button>
              {errorMsg && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-danger)', fontSize: 'var(--fs-sm)', fontWeight: 500 }}>
                  <AlertTriangle size={16} />
                  {errorMsg}
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {mode === 'manual' && (
        <form onSubmit={handlePredictManual} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-5)' }}>
            <Card title="Building Context" action={<Building2 size={16} style={{color: 'var(--text-muted)'}} />}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                <FormGroup label="Site ID"><input className="input" type="number" name="site_id" value={formData.site_id} onChange={handleChange} required /></FormGroup>
                <FormGroup label="Primary Use"><select className="input" name="primary_use" value={formData.primary_use} onChange={handleChange} required>{PRIMARY_USES.map(u => <option key={u} value={u}>{u}</option>)}</select></FormGroup>
                <FormGroup label="Square Feet"><input className="input" type="number" name="square_feet" value={formData.square_feet} onChange={handleChange} required /></FormGroup>
                <FormGroup label="Year Built"><input className="input" type="number" name="year_built" value={formData.year_built} onChange={handleChange} required /></FormGroup>
                <FormGroup label="Floor Count"><input className="input" type="number" name="floor_count" value={formData.floor_count} onChange={handleChange} required /></FormGroup>
                <FormGroup label="Meter"><select className="input" name="meter" value={formData.meter} onChange={handleChange} required>{METER_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}</select></FormGroup>
              </div>
            </Card>

            <Card title="Temporal Context" action={<Clock size={16} style={{color: 'var(--text-muted)'}} />}>
               <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                  <FormGroup label="Hour (0-23)"><input className="input" type="number" min="0" max="23" name="hour" value={formData.hour} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Day of Week (0-6)"><input className="input" type="number" min="0" max="6" name="day_of_week" value={formData.day_of_week} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Month (1-12)"><input className="input" type="number" min="1" max="12" name="month" value={formData.month} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Day of Year (1-365)"><input className="input" type="number" min="1" max="366" name="day_of_year" value={formData.day_of_year} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Is Weekend (0/1)"><input className="input" type="number" min="0" max="1" name="is_weekend" value={formData.is_weekend} onChange={handleChange} required /></FormGroup>
               </div>
            </Card>

            <Card title="Weather Context" action={<CloudRain size={16} style={{color: 'var(--text-muted)'}} />}>
               <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                  <FormGroup label="Air Temp (°C)"><input className="input" type="number" step="any" name="air_temperature" value={formData.air_temperature} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Cloud Coverage"><input className="input" type="number" step="any" name="cloud_coverage" value={formData.cloud_coverage} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Dew Temp (°C)"><input className="input" type="number" step="any" name="dew_temperature" value={formData.dew_temperature} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Precip (mm/1hr)"><input className="input" type="number" step="any" name="precip_depth_1_hr" value={formData.precip_depth_1_hr} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Sea Level Press."><input className="input" type="number" step="any" name="sea_level_pressure" value={formData.sea_level_pressure} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Wind Direction"><input className="input" type="number" step="any" name="wind_direction" value={formData.wind_direction} onChange={handleChange} required /></FormGroup>
                  <FormGroup label="Wind Speed"><input className="input" type="number" step="any" name="wind_speed" value={formData.wind_speed} onChange={handleChange} required /></FormGroup>
               </div>
            </Card>
          </div>

          <Card title="Historical Energy State" action={<Database size={16} style={{color: 'var(--text-muted)'}} />}>
            <div style={{ marginBottom: 'var(--space-4)', padding: 'var(--space-3)', background: 'rgba(6,182,212,0.1)', borderLeft: '3px solid var(--accent-primary)', borderRadius: 'var(--radius-sm)', fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)' }}>
              Historical energy state is required because the deployed model uses autoregressive lag and rolling features. Predictions cannot be generated when these values are unavailable.
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
              <FormGroup label="Lag 1"><input className="input" type="number" step="any" name="lag_1" value={formData.lag_1} onChange={handleChange} required /></FormGroup>
              <FormGroup label="Lag 24"><input className="input" type="number" step="any" name="lag_24" value={formData.lag_24} onChange={handleChange} required /></FormGroup>
              <FormGroup label="Lag 168"><input className="input" type="number" step="any" name="lag_168" value={formData.lag_168} onChange={handleChange} required /></FormGroup>
              <FormGroup label="Rolling Mean 24"><input className="input" type="number" step="any" name="rolling_mean_24" value={formData.rolling_mean_24} onChange={handleChange} required /></FormGroup>
              <FormGroup label="Rolling Mean 168"><input className="input" type="number" step="any" name="rolling_mean_168" value={formData.rolling_mean_168} onChange={handleChange} required /></FormGroup>
              <FormGroup label="Rolling Std 24"><input className="input" type="number" step="any" name="rolling_std_24" value={formData.rolling_std_24} onChange={handleChange} required /></FormGroup>
              <FormGroup label="Rolling Std 168"><input className="input" type="number" step="any" name="rolling_std_168" value={formData.rolling_std_168} onChange={handleChange} required /></FormGroup>
            </div>
          </Card>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            <Button variant="primary" type="submit" disabled={loading} style={{ minWidth: 200, justifyContent: 'center' }}>
              {loading ? 'Generating prediction...' : 'Generate Prediction'}
            </Button>
            {errorMsg && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-danger)', fontSize: 'var(--fs-sm)', fontWeight: 500 }}>
                <AlertTriangle size={16} />
                {errorMsg}
              </div>
            )}
          </div>
        </form>
      )}

      {result && (
        <GlassPanel style={{ marginTop: 'var(--space-4)', padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                 <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.2rem' }}>
                   Predicted Energy
                 </div>
                 <div style={{ fontFamily: 'var(--font-display)', fontSize: '3rem', fontWeight: 700, color: 'var(--accent-primary)', lineHeight: 1 }}>
                   {result.predicted_energy?.toFixed(2)} <span style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{result.unit || 'kWh'}</span>
                 </div>
                 {result.is_demo && (
                   <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                     Actual Consumption: <strong>{result.actual_reading} kWh</strong>
                   </div>
                 )}
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                 <Button variant="outline" size="sm" onClick={() => navigate('/explain')}>Explain Prediction <ArrowRight size={14}/></Button>
                 <Button variant="outline" size="sm" onClick={() => navigate('/drivers')}>View Energy Drivers <ArrowRight size={14}/></Button>
                 <Button variant="outline" size="sm" onClick={() => navigate('/recommendations')}>View Recommendations <ArrowRight size={14}/></Button>
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-5)', borderTop: '1px solid var(--border-subtle)', paddingTop: 'var(--space-5)' }}>
              <div>
                <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Model</div>
                <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>{result.model_name || 'Random Forest'}</div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Feature Group</div>
                <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>{result.feature_group || 'Group B · Historical'}</div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Target</div>
                <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>meter_reading (raw)</div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Context</div>
                <div style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', fontWeight: 500 }}>{result.is_demo ? 'Building 565 / Timestamp 2016-01-08' : 'Manual Entry'}</div>
              </div>
            </div>
            
          </div>
        </GlassPanel>
      )}
    </div>
  );
};
