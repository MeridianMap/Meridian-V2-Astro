import { useState, useEffect } from 'react';
import { getHouseSystems } from '../apiClient';

const useHouseSystems = () => {
  const [houseSystems, setHouseSystems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    getHouseSystems()
      .then((data) => {
        setHouseSystems(data.house_systems || []);
        setError(null);
      })
      .catch((err) => {
        console.error('Error fetching house systems:', err);
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return { houseSystems, loading, error };
};

export default useHouseSystems;
