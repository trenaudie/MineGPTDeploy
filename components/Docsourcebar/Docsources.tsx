import { Docsource } from '@/types/docsource';
import { FC } from 'react';
import { DocsourceComponent } from './Docsource';

interface Props {
  docsources: Docsource[];
  onUpdateDocsource: (docsource: Docsource) => void;
  onDeleteDocsource: (docsource: Docsource) => void;
}

export const Docsources: FC<Props> = ({
  docsources,
  onUpdateDocsource,
  onDeleteDocsource,
}) => {
  return (
    <div className="flex w-full flex-col gap-1">
      {docsources.slice().reverse().map((docsource, index) => (
        <DocsourceComponent
          key={index}
          docsource={docsource}
          onUpdateDocsource={onUpdateDocsource}
          onDeleteDocsource={onDeleteDocsource}
        />
      ))}
    </div>
  );
};
