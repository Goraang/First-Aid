import React, { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../components/auth/AuthContext';
import { Link } from 'react-router-dom';
import { 
  User, Mail, Calendar, Phone, Activity, Microscope, Pill, 
  ChevronRight, Edit2, Check, X, FileText, Heart, AlertCircle, Loader2, Award
} from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

const ProfilePage = () => {
  const { user } = useContext(AuthContext);
  
  // Profile state initialized with default values
  const [profileData, setProfileData] = useState({
    fullName: 'User',
    email: '',
    dateOfBirth: '',
    gender: '',
    phoneNumber: '',
    bloodType: 'O+',
    medicalHistory: '',
    allergies: ''
  });

  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({ ...profileData });
  const [stats, setStats] = useState({ skinAnalyses: null, medicineScans: null });
  const [statsLoading, setStatsLoading] = useState(true);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState({ type: '', text: '' });

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  });

  // Sync profileData with AuthContext user when user changes
  useEffect(() => {
    if (user) {
      // LocalStorage fallback cache for local dev persistence
      const stored = localStorage.getItem(`profile_cache_${user.email}`);
      let fallbackData = {};
      if (stored) {
        try {
          fallbackData = JSON.parse(stored);
        } catch (e) {
          console.error('Failed to parse profile cache', e);
        }
      }

      const mergedData = {
        fullName: user.name || fallbackData.fullName || 'User',
        email: user.email || fallbackData.email || '',
        dateOfBirth: user.dob || fallbackData.dateOfBirth || '',
        gender: user.gender || fallbackData.gender || '',
        phoneNumber: user.phone || fallbackData.phoneNumber || '',
        bloodType: user.blood_type || fallbackData.bloodType || 'O+',
        medicalHistory: user.medical_history || fallbackData.medicalHistory || '',
        allergies: user.allergies || fallbackData.allergies || ''
      };

      setProfileData(mergedData);
      setEditData(mergedData);
    }
  }, [user]);

  // Fetch scan statistics
  useEffect(() => {
    const fetchStats = async () => {
      setStatsLoading(true);
      try {
        const headers = {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        };
        const [dermRes, pharmRes] = await Promise.all([
          fetch(`${API_URL}/api/dermatology/stats`, { headers }),
          fetch(`${API_URL}/api/pharmacy/stats`, { headers })
        ]);

        const dermData = dermRes.ok ? await dermRes.json() : null;
        const pharmData = pharmRes.ok ? await pharmRes.json() : null;

        setStats({
          skinAnalyses: dermData?.total_analyses ?? 0,
          medicineScans: pharmData?.total_scans ?? 0
        });
      } catch (err) {
        console.error('Stats fetch error:', err);
        setStats({ skinAnalyses: 0, medicineScans: 0 });
      } finally {
        setStatsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleEditChange = (field, value) => {
    setEditData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async (e) => {
    if (e) e.preventDefault();
    setSaveLoading(true);
    setSaveMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${API_URL}/api/auth/profile`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          name: editData.fullName,
          dob: editData.dateOfBirth,
          gender: editData.gender,
          phone: editData.phoneNumber,
          blood_type: editData.bloodType,
          medical_history: editData.medicalHistory,
          allergies: editData.allergies
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to update profile');
      }

      const data = await response.json();
      
      const updatedData = {
        fullName: data.user.name,
        email: data.user.email,
        dateOfBirth: data.user.dob,
        gender: data.user.gender,
        phoneNumber: data.user.phone,
        bloodType: data.user.blood_type,
        medicalHistory: data.user.medical_history,
        allergies: data.user.allergies
      };

      setProfileData(updatedData);
      setEditData(updatedData);
      
      // Update local storage backup
      localStorage.setItem(`profile_cache_${data.user.email}`, JSON.stringify(updatedData));
      
      setSaveMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsEditing(false);

      // Auto clear message after 4s
      setTimeout(() => setSaveMessage({ type: '', text: '' }), 4000);
    } catch (err) {
      console.error('Error saving profile:', err);
      setSaveMessage({ type: 'error', text: err.message || 'Error updating profile. Please try again.' });
    } finally {
      setSaveLoading(false);
    }
  };

  const handleCancel = () => {
    setEditData({ ...profileData });
    setIsEditing(false);
    setSaveMessage({ type: '', text: '' });
  };

  const totalScans = (stats.skinAnalyses ?? 0) + (stats.medicineScans ?? 0);

  return (
    <div className="profile-page" id="profile-page">
      {/* Drifting glow orbs for ambient premium effect */}
      <div className="profile-glow-1" />
      <div className="profile-glow-2" />
      <div className="profile-grid-pattern" />

      {/* Header Banner */}
      <div className="profile-header-section">
        <div className="profile-header-content">
          <div className="profile-avatar-wrapper">
            <div className="profile-avatar-large">
              {profileData.fullName.charAt(0).toUpperCase()}
            </div>
            <div className="profile-avatar-ring" />
          </div>
          <div className="profile-header-info">
            <h1 className="text-highlight">{profileData.fullName}</h1>
            <p className="profile-email-badge">
              <Mail size={14} />
              {profileData.email}
            </p>
          </div>
        </div>
      </div>

      <div className="profile-main">
        {/* Save Notifications */}
        {saveMessage.text && (
          <div className={`${saveMessage.type}-message`}>
            {saveMessage.type === 'error' ? <AlertCircle size={18} /> : <Check size={18} />}
            <span>{saveMessage.text}</span>
          </div>
        )}

        {/* Quick Stats Grid */}
        <div className="profile-stats-grid">
          <div className="profile-stat-card border-beam">
            <div className="profile-stat-icon-wrapper text-pink">
              <Microscope size={22} />
            </div>
            <div className="profile-stat-value">
              {statsLoading ? <Loader2 className="spinner" size={20} /> : (stats.skinAnalyses ?? '—')}
            </div>
            <div className="profile-stat-label">Skin Analyses</div>
          </div>

          <div className="profile-stat-card border-beam">
            <div className="profile-stat-icon-wrapper text-teal">
              <Pill size={22} />
            </div>
            <div className="profile-stat-value">
              {statsLoading ? <Loader2 className="spinner" size={20} /> : (stats.medicineScans ?? '—')}
            </div>
            <div className="profile-stat-label">Medicine Scans</div>
          </div>

          <div className="profile-stat-card border-beam">
            <div className="profile-stat-icon-wrapper text-purple">
              <Activity size={22} />
            </div>
            <div className="profile-stat-value">
              {statsLoading ? <Loader2 className="spinner" size={20} /> : totalScans}
            </div>
            <div className="profile-stat-label">Total Operations</div>
          </div>

          <div className="profile-stat-card border-beam">
            <div className="profile-stat-icon-wrapper text-gold">
              <Award size={22} />
            </div>
            <div className="profile-stat-value">Free</div>
            <div className="profile-stat-label">Membership Plan</div>
          </div>
        </div>

        {/* Quick Actions Row */}
        <div className="profile-actions-row">
          <Link to="/dermatology" className="profile-action-card">
            <div className="action-icon-circle bg-pink-ultra text-pink">
              <Microscope size={24} />
            </div>
            <div className="action-card-content">
              <h4>Skin Analysis</h4>
              <p>Upload a photo of your skin for an instant diagnostic run</p>
            </div>
            <ChevronRight className="action-arrow" size={20} />
          </Link>

          <Link to="/pharmacy" className="profile-action-card">
            <div className="action-icon-circle bg-teal-ultra text-teal">
              <Pill size={24} />
            </div>
            <div className="action-card-content">
              <h4>Medicine Scanner</h4>
              <p>Point your camera to scan and identify any pill or box label</p>
            </div>
            <ChevronRight className="action-arrow" size={20} />
          </Link>
        </div>

        {/* Profile Info Details Card */}
        <div className="profile-info-card">
          <div className="profile-info-header">
            <div className="header-title-flex">
              <User className="text-purple" size={20} />
              <h3>Personal Information</h3>
            </div>
            {!isEditing && (
              <button 
                onClick={() => setIsEditing(true)} 
                className="btn btn-outline btn-sm" 
                id="edit-profile-btn"
              >
                <Edit2 size={14} />
                Edit Profile
              </button>
            )}
          </div>

          {isEditing ? (
            <form className="profile-form" onSubmit={handleSave}>
              <div className="profile-form-grid">
                <div className="form-group">
                  <label htmlFor="edit-fullName">Full Name</label>
                  <div className="input-with-icon">
                    <User size={16} className="input-icon" />
                    <input 
                      id="edit-fullName" 
                      type="text" 
                      value={editData.fullName} 
                      onChange={(e) => handleEditChange('fullName', e.target.value)} 
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="edit-dob">Date of Birth</label>
                  <div className="input-with-icon">
                    <Calendar size={16} className="input-icon" />
                    <input 
                      id="edit-dob" 
                      type="date" 
                      value={editData.dateOfBirth} 
                      onChange={(e) => handleEditChange('dateOfBirth', e.target.value)} 
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="edit-gender">Gender</label>
                  <select 
                    id="edit-gender" 
                    value={editData.gender} 
                    onChange={(e) => handleEditChange('gender', e.target.value)}
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="edit-phone">Phone Number</label>
                  <div className="input-with-icon">
                    <Phone size={16} className="input-icon" />
                    <input 
                      id="edit-phone" 
                      type="tel" 
                      value={editData.phoneNumber} 
                      onChange={(e) => handleEditChange('phoneNumber', e.target.value)} 
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="edit-blood">Blood Type</label>
                  <select 
                    id="edit-blood" 
                    value={editData.bloodType} 
                    onChange={(e) => handleEditChange('bloodType', e.target.value)}
                  >
                    {['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'].map(bt => (
                      <option key={bt} value={bt}>{bt}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="edit-history">Medical History</label>
                <div className="textarea-wrapper">
                  <FileText size={16} className="textarea-icon" />
                  <textarea 
                    id="edit-history" 
                    value={editData.medicalHistory} 
                    onChange={(e) => handleEditChange('medicalHistory', e.target.value)} 
                    placeholder="List any chronic conditions, operations, or medical events..." 
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="edit-allergies">Allergies</label>
                <div className="textarea-wrapper">
                  <Heart size={16} className="textarea-icon" />
                  <textarea 
                    id="edit-allergies" 
                    value={editData.allergies} 
                    onChange={(e) => handleEditChange('allergies', e.target.value)} 
                    placeholder="List drug, food, or environmental allergies..." 
                  />
                </div>
              </div>

              <div className="form-actions">
                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  id="save-profile-btn"
                  disabled={saveLoading}
                >
                  {saveLoading ? (
                    <>
                      <Loader2 className="spinner" size={16} />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Check size={16} />
                      Save Changes
                    </>
                  )}
                </button>
                <button 
                  type="button" 
                  onClick={handleCancel} 
                  className="btn btn-secondary" 
                  id="cancel-edit-btn"
                  disabled={saveLoading}
                >
                  <X size={16} />
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="profile-info-display">
              <div className="profile-info-grid">
                <div className="profile-info-item">
                  <span className="profile-info-label">
                    <Calendar size={12} /> Date of Birth
                  </span>
                  <span className="profile-info-value">{profileData.dateOfBirth || '—'}</span>
                </div>
                <div className="profile-info-item">
                  <span className="profile-info-label">
                    <User size={12} /> Gender
                  </span>
                  <span className="profile-info-value">
                    {profileData.gender ? profileData.gender.charAt(0).toUpperCase() + profileData.gender.slice(1) : '—'}
                  </span>
                </div>
                <div className="profile-info-item">
                  <span className="profile-info-label">
                    <Phone size={12} /> Phone Number
                  </span>
                  <span className="profile-info-value">{profileData.phoneNumber || '—'}</span>
                </div>
                <div className="profile-info-item">
                  <span className="profile-info-label">
                    <Activity size={12} /> Blood Type
                  </span>
                  <span className="profile-info-value-badge">{profileData.bloodType}</span>
                </div>
              </div>

              <div className="profile-info-block">
                <span className="profile-info-label">
                  <FileText size={12} /> Medical History
                </span>
                <p className="profile-info-text">
                  {profileData.medicalHistory || 'No past medical conditions provided.'}
                </p>
              </div>

              <div className="profile-info-block">
                <span className="profile-info-label">
                  <Heart size={12} /> Registered Allergies
                </span>
                <p className={`profile-info-text ${profileData.allergies ? 'text-hazard' : ''}`}>
                  {profileData.allergies || 'No allergies recorded.'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
