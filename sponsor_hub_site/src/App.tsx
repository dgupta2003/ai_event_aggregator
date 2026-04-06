import React from 'react';
import SponsorHubNavbar from './components/SponsorHubNavbar';
import SponsorshipHubPage from './components/SponsorshipHubPage';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#030014] text-white font-sans">
      <SponsorHubNavbar />
      <main>
        <SponsorshipHubPage />
      </main>
    </div>
  );
};

export default App;
