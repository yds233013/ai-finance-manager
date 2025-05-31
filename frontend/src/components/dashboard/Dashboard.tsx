import { useEffect, useState } from 'react'
import {
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Heading,
} from '@chakra-ui/react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import axios from 'axios'

interface Transaction {
  id: number
  amount: number
  description: string
  date: string
  category: string
}

const Dashboard = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [totalSpent, setTotalSpent] = useState(0)
  const [monthlyAverage, setMonthlyAverage] = useState(0)

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/v1/transactions/', {
          headers: { Authorization: `Bearer ${token}` },
        })
        setTransactions(response.data)
        
        // Calculate total spent
        const total = response.data.reduce((acc: number, curr: Transaction) => acc + curr.amount, 0)
        setTotalSpent(total)
        
        // Calculate monthly average
        const months = new Set(response.data.map((t: Transaction) => t.date.substring(0, 7))).size
        setMonthlyAverage(total / (months || 1))
      } catch (error) {
        console.error('Error fetching transactions:', error)
      }
    }

    fetchTransactions()
  }, [])

  // Prepare data for the chart
  const chartData = transactions.reduce((acc: any[], transaction: Transaction) => {
    const date = transaction.date.substring(0, 7) // Get YYYY-MM
    const existingEntry = acc.find(entry => entry.date === date)
    
    if (existingEntry) {
      existingEntry.amount += transaction.amount
    } else {
      acc.push({ date, amount: transaction.amount })
    }
    
    return acc
  }, []).sort((a, b) => a.date.localeCompare(b.date))

  return (
    <Box>
      <Heading mb={6}>Financial Overview</Heading>
      
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
        <Stat p={4} shadow="md" border="1px" borderColor="gray.200" borderRadius="md">
          <StatLabel>Total Spent</StatLabel>
          <StatNumber>${totalSpent.toFixed(2)}</StatNumber>
          <StatHelpText>All time</StatHelpText>
        </Stat>
        
        <Stat p={4} shadow="md" border="1px" borderColor="gray.200" borderRadius="md">
          <StatLabel>Monthly Average</StatLabel>
          <StatNumber>${monthlyAverage.toFixed(2)}</StatNumber>
          <StatHelpText>Per month</StatHelpText>
        </Stat>
        
        <Stat p={4} shadow="md" border="1px" borderColor="gray.200" borderRadius="md">
          <StatLabel>Total Transactions</StatLabel>
          <StatNumber>{transactions.length}</StatNumber>
          <StatHelpText>All time</StatHelpText>
        </Stat>
      </SimpleGrid>

      <Box h="400px" mb={8}>
        <Heading size="md" mb={4}>Monthly Spending Trend</Heading>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="amount"
              stroke="#3182ce"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  )
}

export default Dashboard 