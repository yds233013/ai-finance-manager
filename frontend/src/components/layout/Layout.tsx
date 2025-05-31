import { Box, Flex, Link as ChakraLink, Button, Heading } from '@chakra-ui/react'
import { Link as RouterLink, Outlet, useNavigate } from 'react-router-dom'

const Layout = () => {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <Box minH="100vh">
      <Flex
        as="nav"
        align="center"
        justify="space-between"
        wrap="wrap"
        padding="1.5rem"
        bg="blue.500"
        color="white"
      >
        <Flex align="center" mr={5}>
          <Heading as="h1" size="lg">
            Finance Manager
          </Heading>
        </Flex>

        <Flex align="center">
          <ChakraLink
            as={RouterLink}
            to="/"
            mr={4}
            _hover={{ textDecoration: 'none', color: 'blue.100' }}
          >
            Dashboard
          </ChakraLink>
          <ChakraLink
            as={RouterLink}
            to="/transactions"
            mr={4}
            _hover={{ textDecoration: 'none', color: 'blue.100' }}
          >
            Transactions
          </ChakraLink>
          <Button
            variant="outline"
            _hover={{ bg: 'blue.400' }}
            onClick={handleLogout}
          >
            Logout
          </Button>
        </Flex>
      </Flex>

      <Box p={4}>
        <Outlet />
      </Box>
    </Box>
  )
}

export default Layout 