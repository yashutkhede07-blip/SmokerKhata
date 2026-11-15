import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Sparkles } from 'lucide-react';

export const Login: React.FC = () => {
  const [phone, setPhone] = useState('9876543210');
  const [otp, setOtp] = useState('123456');
  const [step, setStep] = useState<'PHONE' | 'OTP'>('PHONE');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (phone.length < 10) return;
    setLoading(true);
    try {
      await fetch('/api/auth/otp/send/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      setStep('OTP');
    } catch (e) {
      // Dev mode fallback
      setStep('OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const resp = await fetch('/api/auth/otp/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp }),
      });
      if (resp.ok) {
        const data = await resp.json();
        localStorage.setItem('sk_access', data.access);
        navigate('/');
      } else {
        navigate('/'); // Bypass for dev / preview
      }
    } catch (e) {
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-sm border border-border bg-surface p-7 rounded-3xl shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 bg-background border border-border rounded-2xl flex items-center justify-center mx-auto text-3xl shadow-xs">
            🚬
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-foreground">SmokerKhata</h1>
            <p className="text-xs text-muted font-medium mt-0.5">
              Smart Shop POS, Stock & Udhaar Khata
            </p>
          </div>
        </div>

        {step === 'PHONE' ? (
          <form onSubmit={handleSendOtp} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-muted block mb-1.5">Owner Mobile Number</label>
              <div className="relative">
                <span className="absolute left-3.5 top-3 text-xs font-bold text-muted font-mono">+91</span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  placeholder="10-digit number"
                  className="w-full h-12 pl-12 pr-3 border border-border rounded-xl bg-background text-foreground font-mono text-base font-bold outline-none focus:ring-2 focus:ring-foreground/20"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || phone.length < 10}
              className="w-full h-12 bg-foreground text-background font-extrabold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center space-x-2 cursor-pointer shadow-xs min-h-touch"
            >
              <span>{loading ? 'Sending SMS OTP...' : 'Send Login OTP'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-muted block mb-1.5 text-center">
                Enter 6-Digit OTP sent to +91 {phone}
              </label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value.slice(0, 6))}
                placeholder="123456"
                className="w-full h-13 px-3 border border-border rounded-xl bg-background text-foreground text-center tracking-widest text-2xl font-extrabold font-mono outline-none focus:ring-2 focus:ring-foreground/20"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading || otp.length < 4}
              className="w-full h-12 bg-foreground text-background font-extrabold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center space-x-2 cursor-pointer shadow-xs min-h-touch"
            >
              <span>{loading ? 'Verifying...' : 'Verify & Open Counter'}</span>
              <ShieldCheck className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => setStep('PHONE')}
              className="w-full text-center text-xs text-muted hover:underline block pt-1 cursor-pointer"
            >
              ← Change Mobile Number
            </button>
          </form>
        )}

        {/* Demo Fast Track Bypass button */}
        <div className="pt-2 border-t border-border">
          <button
            onClick={() => navigate('/')}
            className="w-full py-2.5 px-3 bg-emerald-50 dark:bg-emerald-950/30 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-300 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition-colors cursor-pointer border border-emerald-200 dark:border-emerald-800/40"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Open Counter in Demo Mode (Direct)</span>
          </button>
        </div>
      </div>
    </div>
  );
};
