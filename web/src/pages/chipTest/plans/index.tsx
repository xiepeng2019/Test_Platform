import React from 'react';
import { Result, Card } from '@arco-design/web-react';

const App = () => {
  return (
    <Card
      style={{
        borderRadius: 10,
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
        height: 'calc(100vh - 160px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Result status="500" subTitle="This page isn't working."></Result>
    </Card>
  );
};

export default App;
