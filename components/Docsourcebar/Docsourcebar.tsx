import { Folder } from '@/types/folder';
import { Docsource } from '@/types/docsource';
import {
  IconFolderPlus,
  IconMistOff,
  IconPlus,
} from '@tabler/icons-react';
import { FC, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PromptFolders } from '../Folders/Prompt/PromptFolders';
import { Search } from '../Sidebar/Search';
import { DocsourcebarSettings } from './DocsourcebarSettings';
import { Docsources } from './Docsources';
import React, { useRef } from 'react';
import { ChangeEvent } from 'react';


interface Props {
    docsources: Docsource[];
    folders: Folder[]; //might remove
    onCreateFolder: (name: string) => void;
    onDeleteFolder: (folderId: string) => void;
    onUpdateFolder: (folderId: string, name: string) => void;
    onCreateDocsource: (event: ChangeEvent<HTMLInputElement>) => void;
    onUpdateDocsource: (docsource: Docsource) => void;
    onDeleteDocsource: (docsource: Docsource) => void;
  }
  


  export const Docsourcebar: FC<Props> = ({
    folders,
    docsources,
    onCreateFolder,
    onDeleteFolder,
    onUpdateFolder,
    onCreateDocsource,
    onUpdateDocsource,
    onDeleteDocsource,
  }) => {
    //add translation
    const { t } = useTranslation('docsourcebar');
    const [searchTerm, setSearchTerm] = useState<string>('');
    const [filteredDocsources, setFilteredDocsources] = useState<Docsource[]>(docsources);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleUpdateDocsource = (docsource: Docsource) => {
      onUpdateDocsource(docsource);
      setSearchTerm('');
    };
  
    const handleDeleteDocsource = (docsource: Docsource) => {
      onDeleteDocsource(docsource);
      setSearchTerm('');
    };

    useEffect(() => {
        if (searchTerm) {
            setFilteredDocsources(
            docsources.filter((docsource) => {
              const searchable =
              docsource.name.toLowerCase() +
                ' ' +
                docsource.description.toLowerCase();
            return searchable.includes(searchTerm.toLowerCase());
            }),
          );
        } else {
          setFilteredDocsources(docsources);
        }
      }, [searchTerm, docsources]);


      return (
        <div
          className={`fixed top-0 right-0 z-50 flex h-full w-[260px] flex-none flex-col space-y-2 bg-[#202123] p-2 text-[14px] transition-all sm:relative sm:top-0`}
        >
          <div className="flex items-center">
        <input
          id="fileUploadInput"
          type="file"
          accept=".doc,.docx,.pdf" // Specify accepted file types
          onChange={(event) => {
            console.log("file input changed");
            onCreateDocsource(event);
            setSearchTerm('');
          }}
          style={{ display: "none" }} // Hide the file input element
        />

        
        <label
          htmlFor="fileUploadInput"
          className="text-sidebar flex w-[190px] flex-shrink-0 cursor-pointer select-none items-center gap-3 rounded-md border border-white/20 p-3 text-white transition-colors duration-200 hover:bg-gray-500/10"
        >
          <IconPlus size={16} />
          {t("New Document")}
        </label>

    
            <button
              className="flex items-center flex-shrink-0 gap-3 p-3 ml-2 text-sm text-white transition-colors duration-200 border rounded-md cursor-pointer border-white/20 hover:bg-gray-500/10"
              onClick={() => onCreateFolder(t('New folder'))}
            >
              <IconFolderPlus size={16} />
            </button>
          </div>
    
          {docsources.length > 1 && (
            <Search
              placeholder={t('Search docsources...') || ''}
              searchTerm={searchTerm}
              onSearch={setSearchTerm}
            />
          )}
    
          <div className="flex-grow overflow-auto">
    
            {docsources.length > 0 ? (
              <div className="pt-2">
                <Docsources
                  docsources={filteredDocsources.filter((docsource) => !docsource.folderId)}
                  onUpdateDocsource={handleUpdateDocsource}
                  onDeleteDocsource={handleDeleteDocsource}
                />
              </div>
            ) : (
              <div className="mt-8 text-center text-white opacity-50 select-none">
                <IconMistOff className="mx-auto mb-3" />
                <span className="text-[14px] leading-normal">
                  {t('No docsources.')}
                </span>
              </div>
            )}
          </div>
    
          <DocsourcebarSettings />
        </div>
      );
    };
    