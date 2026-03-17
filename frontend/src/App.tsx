import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FilterProvider } from './hooks/useFilters';
import Layout from './components/layout/Layout';
import LoadingSpinner from './components/ui/LoadingSpinner';

// Lazy-loaded pages for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const CampaignOverview = lazy(() => import('./pages/CampaignOverview'));
const ViewabilityHealth = lazy(() => import('./pages/ViewabilityHealth'));
const AudienceSegments = lazy(() => import('./pages/AudienceSegments'));
const AnomalyAlerts = lazy(() => import('./pages/AnomalyAlerts'));
const Attribution = lazy(() => import('./pages/Attribution'));
const ABTesting = lazy(() => import('./pages/ABTesting'));
const FrequencyReach = lazy(() => import('./pages/FrequencyReach'));

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <FilterProvider>
        <BrowserRouter>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
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
            </Suspense>
          </Layout>
        </BrowserRouter>
      </FilterProvider>
    </QueryClientProvider>
  );
}

export default App;
