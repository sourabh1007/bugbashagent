import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import { styled } from '@mui/material/styles';

const HeaderContainer = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  marginBottom: theme.spacing(3),
  boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(45deg, #3b82f6 0%, #8b5cf6 25%, #ec4899 50%, #f59e0b 75%, #10b981 100%)',
    opacity: 0.1,
    animation: 'gradient-shift 10s ease infinite',
  },
  '@keyframes gradient-shift': {
    '0%, 100%': { transform: 'translateX(-100%) rotate(0deg)' },
    '50%': { transform: 'translateX(100%) rotate(180deg)' },
  },
}));

const BrandContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: theme.spacing(2),
  marginBottom: theme.spacing(2),
  position: 'relative',
  zIndex: 2,
}));

const BrandIcon = styled(Box)(({ theme }) => ({
  fontSize: '4rem',
  filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))',
  animation: 'pulse-glow 3s ease-in-out infinite',
  '@keyframes pulse-glow': {
    '0%, 100%': {
      transform: 'scale(1)',
      filter: 'drop-shadow(0 4px 8px rgba(59, 130, 246, 0.3))',
    },
    '50%': {
      transform: 'scale(1.05)',
      filter: 'drop-shadow(0 6px 12px rgba(139, 92, 246, 0.5))',
    },
  },
}));

const MainTitle = styled(Typography)(({ theme }) => ({
  fontSize: '3.5rem',
  fontWeight: 800,
  background: 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
  margin: 0,
  lineHeight: 1.1,
  textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
}));

const Tagline = styled(Typography)(({ theme }) => ({
  fontSize: '1.25rem',
  color: '#94a3b8',
  fontWeight: 500,
  margin: theme.spacing(0.5, 0, 0, 0),
  fontStyle: 'italic',
}));

const ProblemStatement = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  maxWidth: '800px',
  margin: '0 auto 1rem auto',
  position: 'relative',
  zIndex: 2,
}));

const ProblemText = styled(Typography)(({ theme }) => ({
  fontSize: '1.1rem',
  color: '#cbd5e1',
  lineHeight: 1.6,
  fontWeight: 400,
  margin: 0,
}));

const LiveIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: theme.spacing(1),
  marginTop: theme.spacing(2),
  position: 'relative',
  zIndex: 2,
}));

const LiveDot = styled(Box)(({ theme }) => ({
  width: '8px',
  height: '8px',
  background: '#10b981',
  borderRadius: '50%',
  animation: 'pulse 2s infinite',
  '@keyframes pulse': {
    '0%, 100%': { opacity: 1 },
    '50%': { opacity: 0.3 },
  },
}));

const LiveText = styled(Typography)(({ theme }) => ({
  color: '#10b981',
  fontWeight: 600,
  fontSize: '0.875rem',
}));

function Header() {
  return (
    <Container maxWidth="xl" sx={{ pt: 2 }}>
      <HeaderContainer className="animate-fade-in">
        <BrandContainer>
          <BrandIcon>🔍</BrandIcon>
          <Box>
            <MainTitle variant="h1" component="h1">
              Bug Bash Copilot
            </MainTitle>
            <Tagline>
              Your intelligent assistant for smarter bug bashes
            </Tagline>
          </Box>
        </BrandContainer>
        
        <ProblemStatement>
          <ProblemText>
            Automate and augment your bug bash process with AI-powered test scenario generation and execution. 
            Transform time-consuming manual testing into comprehensive, scalable product validation.
          </ProblemText>
        </ProblemStatement>
        
        <LiveIndicator>
          <LiveDot />
          <LiveText>AI Testing Assistant Active</LiveText>
        </LiveIndicator>
      </HeaderContainer>
    </Container>
  );
}

export default Header;
