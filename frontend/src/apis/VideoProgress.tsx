import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ProgressBar, Modal, Button } from 'react-bootstrap';

interface VideoProgressProps {
  videoName: string;
  onFinished: (isFinished: boolean) => void;
}

const VideoProgress: React.FC<VideoProgressProps> = ({ videoName, onFinished }) => {
  const [progress, setProgress] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [isProgressing, SetIsProgressing] = useState(false);
  const [progressFailed, SetProgressFailed] = useState(false);
  const [dots, setDots] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prevDots) => (prevDots + 1) % 4);
    }, 500);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await axios.get('/api/uploadVideo_status');
        const progressValue = response.data[`video:${videoName}`];
        console.log(progressValue);
        
        if (progressValue && typeof progressValue === 'string' && progressValue.endsWith('%')) {
          SetIsProgressing(true);
        }

        if (progressValue === "100%") {
          setIsGenerating(true);
        } else if (progressValue === "Finished") {
          setIsFinished(true);
          onFinished(true);
          try {
            const response = await axios.post('/api/uploadVideo_status', { name: videoName, progress: "Exclude" });
            console.log('Response:', response.data);
          } catch (error) {
            console.error('Error updating video status:', error);
          }
        } 
        else if (progressValue === "Failed") {
          SetProgressFailed(true);
          SetIsProgressing(false);
        } else {
          if (!progressValue) {
            setProgress(0);
          } else {
            const percentage = parseInt(progressValue, 10);
            setProgress(percentage);
            if (percentage > 0) {
              onFinished(false); // Indica que o progresso começou
            }
          }
        }
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    };

    const interval = setInterval(fetchProgress, 2000);

    return () => clearInterval(interval);
  }, [videoName, onFinished]);

  useEffect(() => {
    if (isFinished) {
      setShowModal(true);
    }
  }, [isFinished]);

  const handleClose = () => {
    SetProgressFailed(false);
    window.location.reload(); 
  };

  return (
    <>
      {progressFailed ? (
        <Modal show={progressFailed} onHide={handleClose}>
          <Modal.Header closeButton>
            <Modal.Title>Upload Falhou</Modal.Title>
          </Modal.Header>
          <Modal.Body>O upload do vídeo '{videoName}' falhou!</Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>
              Fechar
            </Button>
          </Modal.Footer>
        </Modal>
      ) : isProgressing ? ( // Removi as chaves aqui
        <div className="progres-bar-upload-video">
          {isGenerating ? (
            <ProgressBar
              now={100}
              label={`Generating Content for prompt...`}
              animated
              striped
              variant="success"
              style={{ height: '30px' }}
            />
          ) : (
            <ProgressBar
              min={0}
              now={progress}
              label={`${progress}%`}
              animated
              striped
              variant="success"
              style={{ height: '30px' }}
            />
          )}
        </div>
      ) : (
        <div className="uploading_video"> 
          <h5 style={{ color: 'white' }}>Starting Upload of the video{'.'.repeat(dots)}</h5>
        </div>
      )}
    </>
  );
};

export default VideoProgress;
