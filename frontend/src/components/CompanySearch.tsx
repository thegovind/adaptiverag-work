import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';
import { Search, FileText, Calendar, Building2, Download, ExternalLink, Loader2, Globe } from 'lucide-react';

interface DocumentResult {
  id: string;
  title: string;
  company: string;
  document_type: string;
  filing_date: string;
  cik: string;
  url?: string;
  content?: string;
  source?: string;
  last_updated?: string;
}

interface CompanySearchProps {
  onDocumentsFound: (documents: DocumentResult[]) => void;
}

interface SearchFilters {
  company: string;
  documentTypes: string[];
  years: number[];
  searchType: 'company' | 'website';
}

export function CompanySearch({ onDocumentsFound }: CompanySearchProps) {
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    company: '',
    documentTypes: ['10-K'],
    years: [new Date().getFullYear()],
    searchType: 'company'
  });
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<DocumentResult[]>([]);

  const availableDocumentTypes = [
    { value: '10-K', label: '10-K (Annual Report)', description: 'Comprehensive annual business and financial report' },
    { value: '10-Q', label: '10-Q (Quarterly Report)', description: 'Quarterly financial report' },
    { value: '8-K', label: '8-K (Current Report)', description: 'Report of major events or corporate changes' },
    { value: '10-K/A', label: '10-K/A (Annual Report Amendment)', description: 'Amendment to annual report' },
    { value: '10-Q/A', label: '10-Q/A (Quarterly Report Amendment)', description: 'Amendment to quarterly report' },
    { value: 'DEF 14A', label: 'DEF 14A (Proxy Statement)', description: 'Proxy statement for shareholder meetings' },
    { value: '20-F', label: '20-F (Foreign Annual)', description: 'Annual report for foreign companies' }
  ];

  const currentYear = new Date().getFullYear();
  const availableYears = Array.from({ length: 10 }, (_, i) => currentYear - i);

  const searchTypes = [
    { value: 'company', label: 'Company Documents', icon: Building2, description: 'Search SEC filings by company ticker or name' },
    { value: 'website', label: 'Website Content', icon: Globe, description: 'Search and process content from company websites' }
  ];

  const handleDocTypeChange = (docType: string, checked: boolean) => {
    setSearchFilters(prev => ({
      ...prev,
      documentTypes: checked 
        ? [...prev.documentTypes, docType]
        : prev.documentTypes.filter(type => type !== docType)
    }));
  };

  const handleYearChange = (year: number, checked: boolean) => {
    setSearchFilters(prev => ({
      ...prev,
      years: checked 
        ? [...prev.years, year]
        : prev.years.filter(y => y !== year)
    }));
  };

  const selectAllYears = () => {
    setSearchFilters(prev => ({ ...prev, years: availableYears }));
  };

  const clearAllYears = () => {
    setSearchFilters(prev => ({ ...prev, years: [] }));
  };

  const selectRecentYears = () => {
    const recentYears = availableYears.slice(0, 5); // Last 5 years
    setSearchFilters(prev => ({ ...prev, years: recentYears }));
  };

  const selectAllDocTypes = () => {
    setSearchFilters(prev => ({ ...prev, documentTypes: availableDocumentTypes.map(dt => dt.value) }));
  };

  const clearAllDocTypes = () => {
    setSearchFilters(prev => ({ ...prev, documentTypes: [] }));
  };

  const handleSearchTypeChange = (searchType: 'company' | 'website') => {
    setSearchFilters(prev => ({ ...prev, searchType }));
  };

  const handleSearch = async () => {
    if (!searchFilters.company.trim()) {
      console.error('Please enter a company name or ticker');
      return;
    }
    
    if (searchFilters.searchType === 'company' && 
        (searchFilters.documentTypes.length === 0 || searchFilters.years.length === 0)) {
      console.error('Please select at least one document type and year for company search');
      return;
    }
    
    setIsSearching(true);
    setSearchResults([]);
    
    try {
      const response = await fetch('/api/companies/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: searchFilters.company,
          searchType: searchFilters.searchType,
          documentTypes: searchFilters.searchType === 'company' ? searchFilters.documentTypes : undefined,
          years: searchFilters.searchType === 'company' ? searchFilters.years : undefined
        })
      });
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }
      
      const results = await response.json();
      setSearchResults(results.documents || []);
      onDocumentsFound(results.documents || []);
      
      console.log(`Search complete: Found ${results.documents?.length || 0} results for ${searchFilters.company}`);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Card className="p-8 bg-gradient-to-br from-white to-gray-50 border-gray-200 shadow-xl">
      <div className="flex items-center space-x-4 mb-8">
        <div className="w-12 h-12 bg-gradient-to-br from-microsoft-purple to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
          <Search className="h-6 w-6 text-white" />
        </div>
        <div>
          <h3 className="text-2xl font-bold text-microsoft-gray">Document Search & Process</h3>
          <p className="text-gray-600 mt-1">Search for SEC filings and website content, then process them into the vector store with intelligent chunking and metadata extraction</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Search Type Selection */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <label className="block text-sm font-semibold text-gray-800 mb-4">
            Search Type
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {searchTypes.map((type) => {
              const IconComponent = type.icon;
              return (
                <div 
                  key={type.value}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                    searchFilters.searchType === type.value
                      ? 'border-microsoft-purple bg-microsoft-purple/5 shadow-md'
                      : 'border-gray-200 hover:border-microsoft-purple/30 hover:bg-gray-50'
                  }`}
                  onClick={() => handleSearchTypeChange(type.value as 'company' | 'website')}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      searchFilters.searchType === type.value
                        ? 'bg-microsoft-purple text-white'
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      <IconComponent className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800">{type.label}</h4>
                      <p className="text-sm text-gray-600">{type.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Company/Website Input */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <label className="block text-sm font-semibold text-gray-800 mb-3">
            {searchFilters.searchType === 'company' ? 'Company Ticker or Name' : 'Website URL or Company Name'}
          </label>
          <Input
            type="text"
            placeholder={searchFilters.searchType === 'company' 
              ? "e.g., AAPL, Apple Inc., Microsoft Corporation"
              : "e.g., apple.com, https://investor.apple.com, Microsoft Corporation"
            }
            value={searchFilters.company}
            onChange={(e) => setSearchFilters(prev => ({ ...prev, company: e.target.value }))}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full h-12 text-lg border-2 border-gray-200 focus:border-microsoft-purple focus:ring-2 focus:ring-microsoft-purple/20 rounded-lg"
          />
          <p className="text-xs text-gray-500 mt-2">
            {searchFilters.searchType === 'company' 
              ? 'Enter a company ticker symbol or full company name'
              : 'Enter a website URL or company name to search for relevant web content'
            }
          </p>
        </div>

        {/* Document Types - Only show for company search */}
        {searchFilters.searchType === 'company' && (
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-semibold text-gray-800">
                Document Types
              </label>
              <div className="flex space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={selectAllDocTypes}
                  className="text-xs px-3 py-1 h-7"
                >
                  Select All
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={clearAllDocTypes}
                  className="text-xs px-3 py-1 h-7"
                >
                  Clear All
                </Button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {availableDocumentTypes.map((docType) => (
                <div key={docType.value} className="flex items-start space-x-3 p-3 rounded-lg border border-gray-100 hover:border-microsoft-purple/30 hover:bg-microsoft-purple/5 transition-colors">
                  <Checkbox
                    id={docType.value}
                    checked={searchFilters.documentTypes.includes(docType.value)}
                    onCheckedChange={(checked) => handleDocTypeChange(docType.value, checked as boolean)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <label htmlFor={docType.value} className="text-sm font-medium text-gray-800 cursor-pointer block">
                      {docType.label}
                    </label>
                    <p className="text-xs text-gray-500 mt-1">{docType.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Years - Only show for company search */}
        {searchFilters.searchType === 'company' && (
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-semibold text-gray-800">
                Years
              </label>
              <div className="flex space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={selectRecentYears}
                  className="text-xs px-3 py-1 h-7"
                >
                  Recent 5 Years
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={selectAllYears}
                  className="text-xs px-3 py-1 h-7"
                >
                  Select All Years
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={clearAllYears}
                  className="text-xs px-3 py-1 h-7"
                >
                  Clear All Years
                </Button>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {availableYears.map((year) => (
                <div key={year} className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:border-microsoft-purple/30 hover:bg-microsoft-purple/5 transition-colors">
                  <Checkbox
                    id={`year-${year}`}
                    checked={searchFilters.years.includes(year)}
                    onCheckedChange={(checked) => handleYearChange(year, checked as boolean)}
                  />
                  <label htmlFor={`year-${year}`} className="text-sm font-medium text-gray-700 cursor-pointer">
                    {year}
                  </label>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Search Button */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <Button
            onClick={handleSearch}
            disabled={isSearching || !searchFilters.company.trim() || 
              (searchFilters.searchType === 'company' && (searchFilters.documentTypes.length === 0 || searchFilters.years.length === 0))}
            className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-microsoft-purple to-purple-600 hover:from-microsoft-purple/90 hover:to-purple-600/90 shadow-lg hover:shadow-xl transition-all duration-200"
          >
            {isSearching ? (
              <>
                <Loader2 className="h-5 w-5 mr-3 animate-spin" />
                {searchFilters.searchType === 'company' ? 'Searching SEC Filings...' : 'Searching Website Content...'}
              </>
            ) : (
              <>
                <Search className="h-5 w-5 mr-3" />
                {searchFilters.searchType === 'company' ? 'Search SEC Filings' : 'Search Website Content'}
              </>
            )}
          </Button>
          {(!searchFilters.company.trim() || 
            (searchFilters.searchType === 'company' && (searchFilters.documentTypes.length === 0 || searchFilters.years.length === 0))) && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              {searchFilters.searchType === 'company' 
                ? 'Please enter a company name and select at least one document type and year'
                : 'Please enter a website URL or company name to search'
              }
            </p>
          )}
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h4 className="text-xl font-bold text-microsoft-gray">
                Found {searchResults.length} Documents
              </h4>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <FileText className="h-4 w-4" />
                <span>Ready for processing</span>
              </div>
            </div>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {searchResults.map((doc, index) => (
                <div key={index} className="p-5 border border-gray-200 rounded-xl bg-gradient-to-r from-gray-50 to-white hover:from-microsoft-purple/5 hover:to-purple-50 transition-all duration-200 hover:shadow-md">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-8 h-8 bg-microsoft-purple/10 rounded-lg flex items-center justify-center">
                          <FileText className="h-4 w-4 text-microsoft-purple" />
                        </div>
                        <div>
                          <span className="font-semibold text-microsoft-gray text-lg">{doc.company}</span>
                          <span className="ml-2 px-2 py-1 bg-microsoft-purple/10 text-microsoft-purple text-xs font-medium rounded-full">
                            {doc.document_type}
                          </span>
                        </div>
                      </div>
                      <p className="text-gray-700 mb-3 font-medium">{doc.title}</p>
                      <div className="flex items-center space-x-6 text-sm text-gray-600">
                        <span className="flex items-center">
                          <Calendar className="h-4 w-4 mr-2 text-microsoft-purple" />
                          Filed: {doc.filing_date}
                        </span>
                        <span className="flex items-center">
                          <Building2 className="h-4 w-4 mr-2 text-microsoft-purple" />
                          CIK: {doc.cik}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-col space-y-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs px-3 py-1 h-8"
                      >
                        <Download className="h-3 w-3 mr-1" />
                        Process
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs px-3 py-1 h-8"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
