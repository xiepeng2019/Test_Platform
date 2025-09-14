import React, { useState, useEffect } from 'react';
import { Grid } from '@arco-design/web-react';
import ProjectCard, { ProjectProps } from './blocks/project';
import r from '@/utils/requests';

function MyProject() {
  const [data, setData] = useState<ProjectProps[]>(new Array(6).fill({}));
  const [loading, setLoading] = useState(true);

  const { Row, Col } = Grid;

  const getData = async () => {
    setLoading(true);
    const { data } = await r.get('/api/user/projectList').finally(() => {
      setLoading(false);
    });
    setData(data);
  };

  useEffect(() => {
    getData();
  }, []);

  return (
    <Row gutter={12}>
      {data.map((item, index) => (
        <Col
          key={index}
          span={8}
          style={
            index > data.length - 4 && index < data.length
              ? { marginTop: '16px' }
              : {}
          }
        >
          <ProjectCard {...item} loading={loading} />
        </Col>
      ))}
    </Row>
  );
}

export default MyProject;
