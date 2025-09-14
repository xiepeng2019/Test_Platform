import {
  Form,
  Input,
  Checkbox,
  Link,
  Button,
  Space,
  Message,
} from '@arco-design/web-react';
import { FormInstance } from '@arco-design/web-react/es/Form';
import { IconLarkColor, IconLock, IconUser } from '@arco-design/web-react/icon';
import React, { useEffect, useRef, useState } from 'react';
import useStorage from '@/utils/useStorage';
import useLocale from '@/utils/useLocale';
import locale from './locale';
import styles from './style/index.module.less';
import axios from 'axios';
import { getEnvVar } from '@/utils/env';
import { authJwtLoginApiAuthJwtLoginPost } from '@/client';

interface LoginSuccess {
  access_token: string;
  token_type: string;
}

interface LoginError {
  detail: string;
}

const LarkLoginBaseUrl =
  'https://accounts.feishu.cn/open-apis/authen/v1/authorize';

const LarkLoginParams = new URLSearchParams({
  client_id: getEnvVar('REACT_APP_LARK_CLIENT_ID'),
  redirect_uri: getEnvVar('REACT_APP_LARK_REDIRECT_URI'),
  // scope: 'bitable:app:readonly contact:contact',
  state: 'RANDOMSTRING',
});
const LarkLoginUrl = `${LarkLoginBaseUrl}?${LarkLoginParams.toString()}`;

export default function LoginForm() {
  const formRef = useRef<FormInstance>();
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [loginParams, setLoginParams, removeLoginParams] =
    useStorage('loginParams');

  const t = useLocale(locale);

  const [rememberPassword, setRememberPassword] = useState(!!loginParams);

  function afterLoginSuccess(params, res: LoginSuccess) {
    // 记住密码
    if (rememberPassword) {
      setLoginParams(JSON.stringify(params));
    } else {
      removeLoginParams();
    }
    // 记录登录状态
    localStorage.setItem('userStatus', 'login');
    localStorage.setItem('token', `${res.access_token}`);
    // 跳转首页
    window.location.href = '/project';
  }

  function login(params) {
    setErrorMessage('');
    setLoading(true);

    authJwtLoginApiAuthJwtLoginPost({
      body: {
        username: params.username,
        password: params.password,
        grant_type: 'password',
      },
    })
      .then((res) => {
        console.log(res);
        if ('access_token' in res.data) {
          afterLoginSuccess(params, res.data);
        } else {
          console.error(res.data);
        }
      })
      .catch((error) => {
        if (axios.isAxiosError(error)) {
          setErrorMessage(
            `错误信息: ${
              error.response?.data?.detail || t['login.form.login.errMsg']
            }`
          );
        } else {
          setErrorMessage(t['login.form.login.errMsg']);
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }

  function onSubmitClick() {
    // Message.warning('暂未开放...');
    formRef.current
      .validate()
      .then((values) => {
        login(values);
      })
      .catch((error) => {
        console.error(error.message);
      });
  }

  function onLarkLoginClick() {
    window.location.href = LarkLoginUrl;
  }

  // 读取 localStorage，设置初始值
  useEffect(() => {
    const rememberPassword = !!loginParams;
    setRememberPassword(rememberPassword);
    if (formRef.current && rememberPassword) {
      const parseParams = JSON.parse(loginParams);
      formRef.current.setFieldsValue(parseParams);
    }
  }, [loginParams]);

  return (
    <div className={styles['login-form-wrapper']}>
      <div className={styles['login-form-title']}>{t['login.form.title']}</div>
      <div className={styles['login-form-error-msg']}>{errorMessage}</div>
      <Form className={styles['login-form']} layout="vertical" ref={formRef}>
        <Form.Item
          field="username"
          rules={[{ required: true, message: t['login.form.userName.errMsg'] }]}
        >
          <Input
            prefix={<IconUser />}
            placeholder={t['login.form.userName.placeholder']}
            onPressEnter={onSubmitClick}
          />
        </Form.Item>
        <Form.Item
          field="password"
          rules={[{ required: true, message: t['login.form.password.errMsg'] }]}
        >
          <Input.Password
            prefix={<IconLock />}
            placeholder={t['login.form.password.placeholder']}
            onPressEnter={onSubmitClick}
          />
        </Form.Item>
        <Space size={16} direction="vertical">
          <div className={styles['login-form-password-actions']}>
            <Checkbox checked={rememberPassword} onChange={setRememberPassword}>
              {t['login.form.rememberPassword']}
            </Checkbox>
            <Link onClick={() => Message.warning('请联系管理员...')}>
              {t['login.form.forgetPassword']}
            </Link>
          </div>
          <Button
            icon={<IconLarkColor />}
            type="outline"
            long
            onClick={onLarkLoginClick}
            loading={loading}
          >
            {t['login.form.lark-login']}
          </Button>
          <Button type="primary" long onClick={onSubmitClick} loading={loading}>
            {t['login.form.login']}
          </Button>
          <Button
            type="text"
            long
            onClick={() => Message.warning('暂未开放...')}
            className={styles['login-form-register-btn']}
          >
            {t['login.form.register']}
          </Button>
        </Space>
      </Form>
    </div>
  );
}
