import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  School,
  Warning,
  CheckCircle,
  MoreVert,
  Refresh,
  FilterList,
  Download,
  Notifications,
  Assessment,
  Psychology,
  Timeline,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');

  // Fetch dashboard data
  const { data: dashboardData, isLoading, refetch } = useQuery(
    ['dashboard', timeRange],
    async () => {
      const response = await fetch(`/api/dashboard?timeRange=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      return response.json();
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const StatCard = ({ title, value, change, icon, color, subtitle }) => (
    <Card
      sx={{
        height: '100%',
        background: `linear-gradient(135deg, ${alpha(color, 0.1)} 0%, ${alpha(color, 0.05)} 100%)`,
        border: `1px solid ${alpha(color, 0.2)}`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar
            sx={{
              bgcolor: color,
              width: 48,
              height: 48,
              mr: 2,
            }}
          >
            {icon}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" fontWeight="bold">
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {change >= 0 ? (
            <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
          ) : (
            <TrendingDown sx={{ color: 'error.main', mr: 1 }} />
          )}
          <Typography
            variant="body2"
            color={change >= 0 ? 'success.main' : 'error.main'}
            fontWeight="medium"
          >
            {change >= 0 ? '+' : ''}{change}%
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            {subtitle}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  const QuickActions = () => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Assessment />}
              sx={{ mb: 2 }}
              onClick={() => toast.success('Opening Analytics...')}
            >
              Analytics
            </Button>
          </Grid>
          <Grid item xs={6}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<People />}
              sx={{ mb: 2 }}
              onClick={() => toast.success('Opening Students...')}
            >
              Students
            </Button>
          </Grid>
          <Grid item xs={6}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Psychology />}
              sx={{ mb: 2 }}
              onClick={() => toast.success('Opening AI Dashboard...')}
            >
              AI Insights
            </Button>
          </Grid>
          <Grid item xs={6}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Notifications />}
              onClick={() => toast.success('Opening Notifications...')}
            >
              Alerts
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const RecentActivity = () => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight="bold">
            Recent Activity
          </Typography>
          <IconButton size="small" onClick={() => refetch()}>
            <Refresh />
          </IconButton>
        </Box>
        <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
          {dashboardData?.recentActivities?.map((activity, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'center',
                py: 1,
                borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              }}
            >
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  mr: 2,
                  bgcolor: activity.type === 'warning' ? 'warning.main' : 'success.main',
                }}
              >
                {activity.type === 'warning' ? <Warning /> : <CheckCircle />}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" fontWeight="medium">
                  {activity.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {activity.time}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Dashboard Overview
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<FilterList />}
            onClick={handleMenuClick}
          >
            {timeRange === '7d' ? 'Last 7 Days' : timeRange === '30d' ? 'Last 30 Days' : 'Last 90 Days'}
          </Button>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={() => { setTimeRange('7d'); handleMenuClose(); }}>
              Last 7 Days
            </MenuItem>
            <MenuItem onClick={() => { setTimeRange('30d'); handleMenuClose(); }}>
              Last 30 Days
            </MenuItem>
            <MenuItem onClick={() => { setTimeRange('90d'); handleMenuClose(); }}>
              Last 90 Days
            </MenuItem>
          </Menu>
          <Button variant="outlined" startIcon={<Download />}>
            Export
          </Button>
        </Box>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Students"
            value={dashboardData?.totalStudents || 0}
            change={5.2}
            icon={<School />}
            color={theme.palette.primary.main}
            subtitle="from last month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="At Risk Students"
            value={dashboardData?.atRiskStudents || 0}
            change={-2.1}
            icon={<Warning />}
            color={theme.palette.warning.main}
            subtitle="from last month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Interventions"
            value={dashboardData?.interventions || 0}
            change={12.5}
            icon={<Timeline />}
            color={theme.palette.success.main}
            subtitle="this month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${dashboardData?.successRate || 0}%`}
            change={3.8}
            icon={<TrendingUp />}
            color={theme.palette.info.main}
            subtitle="improvement"
          />
        </Grid>
      </Grid>

      {/* Bottom Section */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <QuickActions />
        </Grid>
        <Grid item xs={12} md={8}>
          <RecentActivity />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
