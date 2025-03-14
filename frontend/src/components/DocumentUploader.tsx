import { ChangeEvent, useState } from 'react';
import { BeatLoader } from 'react-spinners';
import insertDocument from '../apis/insertDocument';
import VideoProgress from '../apis/VideoProgress';
import React from 'react';
import { Modal, Button } from 'react-bootstrap';

/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react';

const loaderStyle = css`
  display: block;
  margin: 0 auto;
`;

interface HTMLInputEvent extends ChangeEvent {
  target: HTMLInputElement & EventTarget;
}

type DocumentUploaderProps = {
  setRefreshViewer: (refresh: boolean) => void;
};

const DocumentUploader = ({ setRefreshViewer }: DocumentUploaderProps) => {
  const [selectedFile, setSelectedFile] = useState<File>();
  const [isFilePicked, setIsFilePicked] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [videoName, setVideoName] = useState<string>('');
  const [isVideo, setIsVideo] = useState(false);
  const [showProgress, setShowProgress] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const changeHandler = (event: HTMLInputEvent) => {
    if (event.target && event.target.files) {
      setSelectedFile(event.target.files[0]);
      setIsFilePicked(true);
      const nameWithoutExtension = event.target.files[0].name.split('.').slice(0, -1).join('.');
      if (event.target.files[0].type.startsWith('video/')) { setIsVideo(true); } else { setIsVideo(false); }
      setVideoName(nameWithoutExtension);
      console.log(nameWithoutExtension);
    }
  };

  const handleSubmission = () => {
    if (selectedFile) {
      setIsLoading(true);
      insertDocument(selectedFile).then(() => {
        setRefreshViewer(true);
        setSelectedFile(undefined);
        setIsFilePicked(false);
        setIsLoading(false);
      });
    }
  };

  const handleProgressFinished = (isFinished: boolean) => {
    if (isFinished) {
      setShowProgress(false); 
      setShowModal(true);
    }
  };

  const handleClose = () => {
    setShowModal(false);
    window.location.reload(); 
  };

  return (
    <div className='uploader'>
      <input
        className='uploader__input'
        type='file'
        name='file-input'
        id='file-input'
        accept='.pdf,.txt,.json,.md,.mp4,.avi,.mov,.mp3,.wav'
        onChange={changeHandler}
      />
      <label className='uploader__label' htmlFor='file-input'>
        <svg
          aria-hidden='true'
          focusable='false'
          data-prefix='fas'
          data-icon='upload'
          className='svg-inline--fa fa-upload fa-w-16'
          role='img'
          xmlns='http://www.w3.org/2000/svg'
          viewBox='0 0 512 512'
        >
          <path
            fill='currentColor'
            d='M296 384h-80c-13.3 0-24-10.7-24-24V192h-87.7c-17.8 0-26.7-21.5-14.1-34.1L242.3 5.7c7.5-7.5 19.8-7.5 27.3 0l152.2 152.2c12.6 12.6 3.7 34.1-14.1 34.1H320v168c0 13.3-10.7 24-24 24zm216-8v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h136v8c0 30.9 25.1 56 56 56h80c30.9 0 56-25.1 56-56v-8h136c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z'
          ></path>
        </svg>
        <span>Upload file</span>
      </label>
      {isFilePicked && selectedFile ? (
        <div className='uploader__details'>
          <div className='uploader__details'>
            <p>{selectedFile.name}</p>
          </div>
        </div>
      ) : (
        <div className='uploader__details'>
          <p className='select_file_text' >Select a file to insert</p>
        </div>
      )}

      {isFilePicked && !isLoading && (
        <button className='uploader__btn' onClick={handleSubmission} /* style={{ margin: "0px 0px 16px" }} */>
          Submit
        </button>
      )}
      {isLoading && <BeatLoader color='#00f596' css={loaderStyle}/>}
      {isVideo && showProgress && !isFilePicked && <VideoProgress videoName={videoName} onFinished={handleProgressFinished} />} 
      {showModal && 
        <Modal show={showModal} onHide={handleClose}>
          <Modal.Header closeButton>
            <Modal.Title>Upload Concluído</Modal.Title>
          </Modal.Header>
          <Modal.Body>O upload do vídeo '{videoName}' foi concluído com sucesso!</Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>
              Fechar
            </Button>
          </Modal.Footer>
        </Modal>
      }
    </div>
  );
};

export default DocumentUploader;