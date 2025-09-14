import { Form } from '@arco-design/web-react';


export const useSearchForm = (onSearch: (params: Record<string, any>) => void) => {
  const [form] = Form.useForm();

  const handleSearch = () => {
    const values = form.getFieldsValue();
    onSearch(values);
  };

  const handleReset = () => {
    form.resetFields();
    const values = form.getFieldsValue();
    onSearch(values);
  };

  return {
    form,
    handleSearch,
    handleReset,
  };
};
