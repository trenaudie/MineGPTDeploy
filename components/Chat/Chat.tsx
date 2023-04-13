import { Conversation, Message } from '@/types/chat';
import { KeyValuePair } from '@/types/data';
import { ErrorMessage } from '@/types/error';
import { OpenAIModel, OpenAIModelID } from '@/types/openai';
import { Plugin } from '@/types/plugin';
import { Prompt } from '@/types/prompt';
import { throttle } from '@/utils';
import AuthButtons from './AuthButtons';
import { IconArrowDown, IconClearAll, IconSettings } from '@tabler/icons-react';
import LoginModal from './LoginModal'; // Add this import
import RegisterModal from './RegisterModal';
import { useTranslation } from 'next-i18next';
import { AuthContext } from '../Global/AuthContext';
import {
  FC,
  MutableRefObject,
  memo,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import { Spinner } from '../Global/Spinner';
import { ChatInput } from './ChatInput';
import { ChatLoader } from './ChatLoader';
import { ChatMessage } from './ChatMessage';
import { ErrorMessageDiv } from './ErrorMessageDiv';
import { ModelSelect } from './ModelSelect';
import { SystemPrompt } from './SystemPrompt';
//import useContext 
import { useContext } from 'react';
import { getSecureCookie } from '@/utils/app/cookieTool';
import { SERVER_ADDRESS } from '../Global/Constants';


interface Props {
  conversation: Conversation;
  models: OpenAIModel[];
  apiKey: string;
  serverSideApiKeyIsSet: boolean;
  defaultModelId: OpenAIModelID;
  messageIsStreaming: boolean;
  modelError: ErrorMessage | null;
  loading: boolean;
  prompts: Prompt[];
  onSend: (
    message: Message,
    deleteCount: number,
    plugin: Plugin | null,
  ) => void;
  onUpdateConversation: (
    conversation: Conversation,
    data: KeyValuePair,
  ) => void;
  onEditMessage: (message: Message, messageIndex: number) => void;
  stopConversationRef: MutableRefObject<boolean>;
}


export const Chat: FC<Props> = memo(
  ({
    conversation,
    models,
    apiKey,
    serverSideApiKeyIsSet,
    defaultModelId,
    messageIsStreaming,
    modelError,
    loading,
    prompts,
    onSend,
    onUpdateConversation,
    onEditMessage,
    stopConversationRef,
  }) => {
    const { t } = useTranslation('chat');
    const [currentMessage, setCurrentMessage] = useState<Message>();
    const [autoScrollEnabled, setAutoScrollEnabled] = useState<boolean>(true);
    const [showSettings, setShowSettings] = useState<boolean>(false);
    const [showScrollDownButton, setShowScrollDownButton] =
      useState<boolean>(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [showLoginModal, setShowLoginModal] = useState(false);
    const [showRegisterModal, setShowRegisterModal] = useState(false);
    const { authenticated, handleLogin,handleLogout } = useContext(AuthContext);
    const [isLoading, setIsLoading] = useState(true);


    const scrollToBottom = useCallback(() => {
      if (autoScrollEnabled) {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        textareaRef.current?.focus();
      }
    }, [autoScrollEnabled]);


    const handleLoginClick = () => {
      const access_token = getSecureCookie('access_token');
      console.log(`inside handleLoginClick`)
      if (access_token) {
        //send fetch request for auto-login
        //if successful, set authenticated to true
        //if not, show login modal
        fetch(`${SERVER_ADDRESS}/auto-login`, {
          method: 'POST',
          headers:{
            'Authorization': `Bearer ${access_token}`
          }
        })
        .then(response => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error('Network response was not ok');
          }
        })
        .then(data => {
          if (data.status === 'authenticated') {
            // JWT token is valid - display user's uploaded documents
            handleLogin(data);
          } else {
            throw new Error('User is not authenticated');
            window.location.replace('/login');
          }
        })
        .catch(error => {
          console.error(error);
        });
      
      setShowLoginModal(true);
      // Add your login functionality here
    };}


    const closeLoginModal = () => {
      setShowLoginModal(false);
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
      }, 1000); // Display the spinner for 1 second (1000 ms)
    };

    const handleRegisterClick = () => {
      setShowRegisterModal(true);
    };

    const closeRegisterModal = () => {
      setShowRegisterModal(false);
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
      }, 1000); // Display the spinner for 1 second (1000 ms)
    };


    const handleScroll = () => {
      if (chatContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } =
          chatContainerRef.current;
        const bottomTolerance = 30;

        if (scrollTop + clientHeight < scrollHeight - bottomTolerance) {
          setAutoScrollEnabled(false);
          setShowScrollDownButton(true);
        } else {
          setAutoScrollEnabled(true);
          setShowScrollDownButton(false);
        }
      }
    };

    const handleScrollDown = () => {
      chatContainerRef.current?.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    };

    const handleSettings = () => {
      setShowSettings(!showSettings);
    };

    const onClearAll = () => {
      if (confirm(t<string>('Are you sure you want to clear all messages?'))) {
        onUpdateConversation(conversation, { key: 'messages', value: [] });
      }
    };

    const scrollDown = () => {
      if (autoScrollEnabled) {
        messagesEndRef.current?.scrollIntoView(true);
      }
    };
    const throttledScrollDown = throttle(scrollDown, 250);

    useEffect(() => {
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 1000); // Display the spinner for 1 second (1000 ms)

      return () => {
        clearTimeout(timer);
      };
    }, []);

    useEffect(() => {
      throttledScrollDown();
      setCurrentMessage(
        conversation.messages[conversation.messages.length - 2],
      );
    }, [conversation.messages, throttledScrollDown]);

    useEffect(() => {
      const observer = new IntersectionObserver(
        ([entry]) => {
          setAutoScrollEnabled(entry.isIntersecting);
          if (entry.isIntersecting) {
            textareaRef.current?.focus();
          }
        },
        {
          root: null,
          threshold: 0.5,
        },
      );
      const messagesEndElement = messagesEndRef.current;
      if (messagesEndElement) {
        observer.observe(messagesEndElement);
      }
      return () => {
        if (messagesEndElement) {
          observer.unobserve(messagesEndElement);
        }
      };
    }, [messagesEndRef]);

    return (
      <div className="relative flex-1 overflow-hidden bg-white dark:bg-[#343541]">
        {!authenticated ? (
          <div className="mx-auto flex h-full w-[300px] flex-col justify-center space-y-6 sm:w-[600px]">
            <div className="text-center text-4xl font-bold text-black dark:text-white">
              Bienvenue sur MineGPT
            </div>
            <div className="text-center text-lg text-black dark:text-white">
              <div className="mb-8">{`Chatbot UI is an open source clone of OpenAI's ChatGPT UI.`}</div>
              <div className="mb-2 font-bold">
                Posez vos questions par rapport aux cours des Mines et recevez une réponse sourcée !
              </div>
            </div>
            <div className="text-center text-gray-500 dark:text-gray-400">
              <div className="mb-2">
                Vous pouvez même uploader vos propres documents et leur poser des questions !
              </div>
              <div className="mb-2">
                Veillez à n'uploader que des fichiers opensource pour des questions de confdentialité.
              </div>
              <div className="mb-2">
                {t(
                  'Idéal pour trouver les informations dont on a besoin',
                )}
              </div>
              <div>
                {t(
                  "sans passer des heures à les chercher dans ses cours ",
                )}

              </div>
              <AuthButtons
                onLoginClick={handleLoginClick}
                onRegisterClick={handleRegisterClick}
              />
            </div>
            <LoginModal onClose={closeLoginModal} show={showLoginModal} />
            <RegisterModal onClose={closeRegisterModal} show={showRegisterModal} />
          </div>
        ) : modelError ? (
          <ErrorMessageDiv error={modelError} />
        ) : (
          <>
            <div
              className="max-h-full overflow-x-hidden"
              ref={chatContainerRef}
              onScroll={handleScroll}
            >
              {conversation.messages.length === 0 ? (
                <>
                  <div className="mx-auto flex w-[350px] flex-col space-y-10 pt-12 sm:w-[600px]">
                    <div className="text-center text-3xl font-semibold text-gray-800 dark:text-gray-100">
                      {isLoading ? (
                        <div>
                          <Spinner size="16px" className="mx-auto" />
                        </div>
                      ) : (
                        'MineGPT'
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex justify-center border border-b-neutral-300 bg-neutral-100 py-2 text-sm text-neutral-500 dark:border-none dark:bg-[#444654] dark:text-neutral-200">
                    {t('Model')}: {conversation.model.name}
                    <button
                      className="ml-2 cursor-pointer hover:opacity-50"
                      onClick={handleSettings}
                    >
                      <IconSettings size={18} />
                    </button>
                    <button
                      className="ml-2 cursor-pointer hover:opacity-50"
                      onClick={onClearAll}
                    >
                      <IconClearAll size={18} />
                    </button>
                  </div>
                  {showSettings && (
                    <div className="flex flex-col space-y-10 md:mx-auto md:max-w-xl md:gap-6 md:py-3 md:pt-6 lg:max-w-2xl lg:px-0 xl:max-w-3xl">
                      <div className="flex h-full flex-col space-y-4 border-b border-neutral-200 p-4 dark:border-neutral-600 md:rounded-lg md:border">
                        <ModelSelect
                          model={conversation.model}
                          models={models}
                          defaultModelId={defaultModelId}
                          onModelChange={(model) =>
                            onUpdateConversation(conversation, {
                              key: 'model',
                              value: model,
                            })
                          }
                        />
                      </div>
                    </div>
                  )}

                  {conversation.messages.map((message, index) => (
                    <ChatMessage
                      key={index}
                      message={message}
                      messageIndex={index}
                      onEditMessage={onEditMessage}
                    />
                  ))}

                  {loading && <ChatLoader />}

                  <div
                    className="h-[162px] bg-white dark:bg-[#343541]"
                    ref={messagesEndRef}
                  />
                </>
              )}
            </div>

            <ChatInput
              stopConversationRef={stopConversationRef}
              textareaRef={textareaRef}
              messageIsStreaming={messageIsStreaming}
              conversationIsEmpty={conversation.messages.length === 0}
              model={conversation.model}
              prompts={prompts}
              onSend={(message, plugin) => {
                setCurrentMessage(message);
                onSend(message, 0, plugin);
              }}
              onRegenerate={() => {
                if (currentMessage) {
                  onSend(currentMessage, 2, null);
                }
              }}
            />
          </>
        )}
        {showScrollDownButton && (
          <div className="absolute bottom-0 right-0 mb-4 mr-4 pb-20">
            <button
              className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-300 text-gray-800 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-neutral-200"
              onClick={handleScrollDown}
            >
              <IconArrowDown size={18} />
            </button>
          </div>
        )}
      </div>
    );
  },
);
Chat.displayName = 'Chat';
