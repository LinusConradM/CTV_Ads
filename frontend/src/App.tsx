import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FilterProvider } from './hooks/useFilters';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import CampaignOverview from './pages/CampaignOverview';
import ViewabilityHealth from './pages/ViewabilityHealth';
import AudienceSegments from './pages/AudienceSegments';
import AnomalyAlerts from './pages/AnomalyAlerts';
import Attribution from './pages/Attribution';
import ABTesting from './pages/ABTesting';
import FrequencyReach from './pages/FrequencyReach';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <FilterProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/campaigns" element={<CampaignOverview />} />
              <Route path="/viewability" element={<ViewabilityHealth />} />
              <Route path="/segments" element={<AudienceSegments />} />
              <Route path="/anomalies" element={<AnomalyAlerts />} />
              <Route path="/attribution" element={<Attribution />} />
              <Route path="/ab-testing" element={<ABTesting />} />
              <Route path="/frequency" element={<FrequencyReach />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </FilterProvider>
    </QueryClientProvider>
  );
}

export default App;
