import { Docsource } from '@/types/docsource';

export const updateDocsource = (updatedDocsource: Docsource, allDocsources: Docsource[]) => {
  const updatedDocsources = allDocsources.map((c) => {
    if (c.id === updatedDocsource.id) {
      return updatedDocsource;
    }

    return c;
  });

  saveDocsources(updatedDocsources);

  return {
    single: updatedDocsource,
    all: updatedDocsources,
  };
};

export const saveDocsources = (docsources: Docsource[]) => {
  localStorage.setItem('docsources', JSON.stringify(docsources));
};
