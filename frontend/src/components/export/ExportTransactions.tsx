import React, { useState } from 'react';
import axios from 'axios';
import { DatePicker } from '@mui/x-date-pickers';
import { TextField, Button, FormControl, InputLabel, Select, MenuItem, Box } from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import type { TextFieldProps } from '@mui/material/TextField';

interface ExportTransactionsProps {
  token: string;
}

const ExportTransactions: React.FC<ExportTransactionsProps> = ({ token }) => {
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [format, setFormat] = useState<string>('csv');
  const [loading, setLoading] = useState<boolean>(false);

  const handleExport = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate.toISOString());
      if (endDate) params.append('end_date', endDate.toISOString());

      const response = await axios({
        url: `/api/export/transactions/${format}?${params.toString()}`,
        method: 'GET',
        responseType: 'blob',
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `transactions_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      // Handle error (show notification, etc.)
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card fade-in">
      <h3>Export Transactions</h3>
      <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
        <Box>
          <DatePicker
            label="Start Date"
            value={startDate}
            onChange={(newValue: Date | null) => setStartDate(newValue)}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </Box>
        
        <Box>
          <DatePicker
            label="End Date"
            value={endDate}
            onChange={(newValue: Date | null) => setEndDate(newValue)}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </Box>

        <FormControl fullWidth>
          <InputLabel>Format</InputLabel>
          <Select
            value={format}
            label="Format"
            onChange={(e: SelectChangeEvent) => setFormat(e.target.value)}
          >
            <MenuItem value="csv">CSV</MenuItem>
            <MenuItem value="excel">Excel</MenuItem>
            <MenuItem value="json">JSON</MenuItem>
          </Select>
        </FormControl>

        <Box sx={{ display: 'flex', alignItems: 'flex-end' }}>
          <Button
            variant="contained"
            onClick={handleExport}
            disabled={loading}
            className={`export-btn ${loading ? 'loading' : ''}`}
            fullWidth
          >
            {loading ? 'Exporting...' : 'Export'}
          </Button>
        </Box>
      </div>
    </div>
  );
};

export default ExportTransactions; 