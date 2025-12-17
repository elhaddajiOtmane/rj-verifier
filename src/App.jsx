import React, { useState, useEffect, useRef } from 'react';
import './index.css';

function App() {
    const [schools, setSchools] = useState([]);
    const [logs, setLogs] = useState([]);
    const [isVerifying, setIsVerifying] = useState(false);
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        schoolId: '',
        verificationId: '',
        docType: 'pdf',
        docStyle: 'nyc',
        schoolName: 'Hudson County Community College',
        address: '70 Sip Ave, Jersey City, NJ 07306',
        logoPath: 'C:\\laragon\\www\\rj-verifier\\engine\\assets\\NYC_DOE_Logo.png',
        savePath: 'C:\\laragon\\www\\rj-verifier\\output'
    });
    const [result, setResult] = useState(null);
    const logEndRef = useRef(null);

    const [activeTab, setActiveTab] = useState('verify');
    const [genResult, setGenResult] = useState(null);

    const [config, setConfig] = useState(null);

    useEffect(() => {
        if (window.api) {
            window.api.getConfig().then(cfg => {
                setConfig(cfg);
            });

            window.api.getSchools().then((data) => {
                if (Array.isArray(data)) {
                    const schoolsWithDefault = [
                        { id: '', name: 'Default (Random Rotation)' },
                        ...data
                    ];
                    setSchools(schoolsWithDefault);
                    setFormData(prev => ({ ...prev, schoolId: '' }));
                }
            });

            window.api.onLogUpdate((msg) => {
                processLog(msg);
            });
        }
    }, [activeTab]);

    const shortenSchoolName = (name) => {
        return name.replace("Springfield High School", "Springfield HS")
            .replace("(Springfield, ", "(");
    };

    const processLog = (msg) => {
        let pMsg = msg.trim();

        try {
            pMsg = JSON.parse(`"${pMsg}"`);
        } catch (e) {
        }
        pMsg = pMsg.replace(/^\[INFO\]\s*/, "")
            .replace(/^\[ERROR\]\s*/, "")
            .replace(/^\[WARNING\]\s*/, "");

        if (pMsg.includes("Failed (Status") && pMsg.includes("{")) {
            try {
                const jsonStart = pMsg.indexOf("{");
                const jsonStr = pMsg.substring(jsonStart).replace(/'/g, '"').replace(/None/g, 'null');
                const errObj = JSON.parse(jsonStr);

                if (errObj.systemErrorMessage) {
                    pMsg = `Error: ${errObj.systemErrorMessage}`;
                } else if (errObj.message) {
                    pMsg = `Error: ${errObj.message}`;
                } else {
                    pMsg = `Error: ${pMsg.substring(0, 50)}...`;
                }
            } catch (e) {
                pMsg = `${pMsg.split("{")[0]}`;
            }
        }

        pMsg = pMsg.replace("✗", "❌").replace("\\u2717", "");

        if (pMsg.startsWith('[{"id":')) return;
        if (pMsg.includes("HTTP Request")) return;
        if (pMsg.includes("Auto-extracted")) return;
        if (pMsg.includes('"success": true') && pMsg.includes('"files":')) return;
        if (!pMsg) return;

        if (pMsg.startsWith("Teacher Info:")) pMsg = `Name: ${pMsg.replace("Teacher Info:", "").trim()}`;
        else if (pMsg.startsWith("Email:")) pMsg = `Email: ${pMsg.replace("Email:", "").trim()}`;
        else if (pMsg.startsWith("School:")) pMsg = `School: ${pMsg.replace("School:", "").trim()}`;
        else if (pMsg.startsWith("DOB:")) pMsg = `DOB: ${pMsg.replace("DOB:", "").trim()}`;
        else if (pMsg.startsWith("Verification ID:")) pMsg = `ID: ${pMsg.replace("Verification ID:", "").trim()}`;
        else if (pMsg.startsWith("Backup:")) pMsg = `Saved: ${pMsg.replace("Backup:", "").trim()}`;

        else if (pMsg.includes("Step 1/4")) pMsg = "Generating PDF...";
        else if (pMsg.includes("Step 2/4")) pMsg = "Submitting Info...";
        else if (pMsg.includes("Step 3/4")) pMsg = "Skipping SSO...";
        else if (pMsg.includes("Step 4/4")) pMsg = "4Uploading Doc...";
        else if (pMsg.startsWith("Complete:")) pMsg = `${pMsg}`;

        else if (pMsg.includes("[OK]")) pMsg = `${pMsg.replace("[OK]", "").trim()}`;

        else if (pMsg.includes("Starting verification for")) return;

        setLogs(prev => {
            const lastLog = prev[prev.length - 1];
            if (lastLog) {
                const lastContent = lastLog.substring(lastLog.indexOf("] ") + 2);
                if (lastContent === pMsg) return prev;
            }
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            return [...prev, `[${time}] ${pMsg}`];
        });
    };

    useEffect(() => {
        logEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleBrowseLogo = async () => {
        const path = await window.api.selectFile();
        if (path) setFormData(prev => ({ ...prev, logoPath: path }));
    };

    const handleBrowseSave = async () => {
        const path = await window.api.selectFolder();
        if (path) setFormData(prev => ({ ...prev, savePath: path }));
    };

    const handleVerify = async () => {
        if (!formData.verificationId) {
            processLog("Error: Verification ID required");
            return;
        }
        setIsVerifying(true);
        setResult(null);
        setLogs([]);
        processLog("Starting...");

        try {
            const res = await window.api.startVerify(formData);
            setResult(res);
            if (res.success) {
                processLog("SUCCESS! Verif Pending.");
            } else {
                processLog(`FAILED: ${res.message}`);
            }
        } catch (err) {
            processLog(`SYS ERROR: ${err}`);
        } finally {
            setIsVerifying(false);
        }
    };

    const handleGenerate = async () => {
        setIsVerifying(true);
        setGenResult("Generating...");
        try {
            const res = await window.api.generateDocs(formData);
            if (res.success) {
                setGenResult(`Saved ${res.files.length} files`);
            } else {
                setGenResult(`Failed: ${res.message}`);
            }
        } catch (err) {
            setGenResult(`Error: ${err}`);
        } finally {
            setIsVerifying(false);
        }
    };

    return (
        <div className="app-container">

            <div className="tab-container" style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '15px', height: '25px' }}>
                <button
                    className={`tab-btn ${activeTab === 'verify' ? 'active' : ''}`}
                    onClick={() => setActiveTab('verify')}
                    title="Verifier Mode"
                    style={{
                        width: '50px', padding: '8px', borderRadius: '4px', cursor: 'pointer', fontSize: '10px',
                        background: activeTab === 'verify' ? '#079183' : '#333', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--bgcard)'
                    }}
                >
                    🔍
                </button>
                <button
                    className={`tab-btn ${activeTab === 'generate' ? 'active' : ''}`}
                    onClick={() => setActiveTab('generate')}
                    title="Generator Mode"
                    style={{
                        width: '50px', padding: '8px', borderRadius: '4px', cursor: 'pointer', fontSize: '10px',
                        background: activeTab === 'generate' ? '#079183' : '#333', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--bgcard)'
                    }}
                >
                    📝
                </button>
            </div>

            {activeTab === 'verify' && (
                <div className="form-group">
                    <label>Your SheerID</label>
                    <input
                        type="text"
                        name="verificationId"
                        placeholder="Paste URL or ID"
                        value={formData.verificationId}
                        onChange={handleChange}
                    />
                </div>
            )}

            {activeTab === 'generate' && (
                <div className="row">
                    <div className="form-group half">
                        <label>School Name</label>
                        <input
                            type="text"
                            name="schoolName"
                            placeholder="e.g. Springfield High School"
                            value={formData.schoolName || ''}
                            onChange={handleChange}
                        />
                    </div>
                    <div className="form-group half">
                        <label>Address</label>
                        <input
                            type="text"
                            name="address"
                            placeholder="e.g. 123 Main St, NY"
                            value={formData.address || ''}
                            onChange={handleChange}
                        />
                    </div>
                </div>
            )}

            <div className="row">
                <div className="form-group half">
                    <label>First Name</label>
                    <input type="text" name="firstName" placeholder="empty for auto generate" value={formData.firstName} onChange={handleChange} />
                </div>
                <div className="form-group half">
                    <label>Last Name</label>
                    <input type="text" name="lastName" placeholder="empty for auto generate" value={formData.lastName} onChange={handleChange} />
                </div>
            </div>

            <div className="row">
                <div className="form-group half" >
                    <label>Email</label>
                    <input
                        type="text"
                        name="email"
                        placeholder="empty for auto generate"
                        value={formData.email}
                        onChange={handleChange}
                    />
                </div>
                <div className="form-group half" >
                    <label>{activeTab === 'generate' ? 'Logo' : 'School'}</label>
                    {activeTab === 'verify' ? (
                        <CustomSelect
                            options={schools.map(s => ({
                                value: s.id,
                                label: s.id === '' ? s.name : shortenSchoolName(s.name)
                            }))}
                            value={formData.schoolId}
                            onChange={(val) => setFormData(prev => ({ ...prev, schoolId: val }))}
                        />
                    ) : (
                        <div style={{ display: 'flex', gap: '5px' }}>
                            <div style={{ flex: 1, position: 'relative' }}>
                                <input type="text" readOnly placeholder="empty for default logo" value={formData.logoPath ? '...' + formData.logoPath.slice(-15) : ''} style={{ width: '100%', paddingRight: '25px' }} />
                                <button onClick={handleBrowseLogo} style={{ position: 'absolute', right: 0, top: 0, bottom: 0, background: '#444', border: 'none', color: 'white', cursor: 'pointer', padding: '0 8px', borderRadius: '2px' }}>📂</button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="row">
                <div className="form-group half">
                    <label>Document</label>
                    <CustomSelect
                        options={[
                            { value: 'pdf', label: 'PDF Only' },
                            { value: 'png', label: 'PNG Only' },
                            { value: 'both', label: 'PNG + PDF' }
                        ]}
                        value={formData.docType}
                        onChange={(val) => setFormData(prev => ({ ...prev, docType: val }))}
                    />
                </div>
                <div className="form-group half">
                    <label>Doc Style</label>
                    <CustomSelect
                        options={
                            activeTab === 'verify'
                                ? [
                                    { value: 'modern', label: 'Payslip Modern' },
                                    { value: 'original', label: 'Payslip Original' },
                                    { value: 'simple', label: 'Payslip Simple' },
                                    { value: 'portal', label: 'Portal Home' },
                                    { value: 'nyc', label: 'NYC DOE Paystub' }
                                ]
                                : [
                                    { value: 'modern', label: 'Payslip Modern' },
                                    { value: 'original', label: 'Payslip Original' },
                                    { value: 'simple', label: 'Payslip Simple' },
                                    { value: 'nyc', label: 'NYC DOE Paystub' }
                                ]
                        }
                        value={formData.docStyle}
                        onChange={(val) => setFormData(prev => ({ ...prev, docStyle: val }))}
                    />
                </div>
            </div>

            {activeTab === 'generate' && (
                <div className="form-group">
                    <label>Save To</label>
                    <div style={{ display: 'flex', gap: '5px' }}>
                        <input type="text" readOnly placeholder="empty for default (output folder)" value={formData.savePath || ''} style={{ flex: 1 }} />
                        <button onClick={handleBrowseSave} style={{ background: '#444', border: 'none', color: 'white', cursor: 'pointer', padding: '0 10px', borderRadius: '4px' }}>Browse</button>
                    </div>
                </div>
            )}

            <button
                className={`verify-btn ${isVerifying ? 'disabled' : ''}`}
                onClick={activeTab === 'verify' ? handleVerify : handleGenerate}
                disabled={isVerifying}
            >
                {isVerifying ? 'RUNNING...' : (activeTab === 'verify' ? 'START VERIFY' : 'GENERATE DOCS')}
            </button>


            <div className="log-window">
                {logs.length === 0 && <div style={{ textAlign: 'center', marginTop: '20px', opacity: 0.5 }}>No active tasks</div>}
                {logs.map((log, i) => (
                    <div key={i} className="log-line">{log}</div>
                ))}
                <div ref={logEndRef} />
            </div>

            <div className="footer">
                This tool is FREE. If you paid, you were scammed.
                <br />
                Official version only available at: <a href="#" onClick={(e) => { e.preventDefault(); window.open('https://s.id/riiicil', '_blank'); }}>s.id/riiicil</a>
                <br /><br />
                &copy; Riiicil 2025 - All rights reserved.
            </div>

        </div>
    );
}

const CustomSelect = ({ options, value, onChange }) => {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (containerRef.current && !containerRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const selectedOption = options.find(opt => opt.value === value) || options[0];

    return (
        <div className="custom-select-container" ref={containerRef}>
            <div className="custom-select-trigger" onClick={() => setIsOpen(!isOpen)}>
                <span>{selectedOption ? selectedOption.label : 'Select...'}</span>
            </div>
            {isOpen && (
                <div className="custom-options">
                    {options.map((option) => (
                        <div
                            key={option.value}
                            className={`custom-option ${option.value === value ? 'selected' : ''}`}
                            onClick={() => {
                                onChange(option.value);
                                setIsOpen(false);
                            }}
                        >
                            {option.label}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default App;
