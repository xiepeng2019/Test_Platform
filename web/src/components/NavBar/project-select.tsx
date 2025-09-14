import React, { useEffect } from 'react';
import { Select, Message } from '@arco-design/web-react';
import { listProjectOptions } from '@/client';
import { useLocation } from 'react-router-dom';
import styles from './style/index.module.less';

const ProjectSelect = () => {
  const [projectsOptions, setProjectsOptions] = React.useState([]);
  const location = useLocation();

  useEffect(() => {
    listProjectOptions().then((res) => {
      setProjectsOptions(res.data);
    });
  }, [location.pathname]);

  function reloadPage() {
    window.location.reload();
  }

  return (
    <Select
      className={styles['project-select']}
      labelInValue
      notFoundContent="No project"
      placeholder="Select project"
      bordered={false}
      defaultValue={localStorage.getItem('projectName')}
      options={projectsOptions.map((project) => ({
        label: project.name,
        value: project.id,
      }))}
      onChange={(value) => {
        console.log(value)
        localStorage.setItem('projectName', value.label);
        localStorage.setItem('projectID', value.value);
        Message.info({
          content: `切换项目 ${value.label}.`,
          showIcon: true,
        });
        reloadPage();
      }}
    />
  );
};

export default ProjectSelect;
