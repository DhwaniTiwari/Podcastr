import { GeneratePodcastProps } from '@/types'
import React, { useState } from 'react'
import { Label } from './ui/label'
import { Textarea } from './ui/textarea'
import { Button } from './ui/button'
import { Loader } from 'lucide-react'
import { useAction, useMutation } from 'convex/react'
import { api } from '@/convex/_generated/api'
import { v4 as uuidv4 } from 'uuid';
import { useToast } from "@/components/ui/use-toast"

import { useUploadFiles } from '@xixixao/uploadstuff/react';

// Renamed custom hook for clarity (optional, but good practice)
const useGenerateElevenLabsAudio = ({
  setAudio, voiceType, voicePrompt, setAudioStorageId, setAudioDuration
}: GeneratePodcastProps) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast()

  const generateUploadUrl = useMutation(api.files.generateUploadUrl);
  const { startUpload } = useUploadFiles(generateUploadUrl)

  // ⭐ CRITICAL FIX: Changed 'api.gemini' to 'api.elevenlabs'
  const getPodcastAudio = useAction(api.elevenlabs.generateAudioAction) 

  const getAudioUrl = useMutation(api.podcasts.getUrl);

  const generatePodcast = async () => {
    setIsGenerating(true);
    setAudio('');
    setAudioStorageId(null);
    setAudioDuration(0);

    if(!voicePrompt) {
      toast({
         title: "Please provide text to generate audio",
      })
     return setIsGenerating(false);
   }
    
    if(!voiceType) {
        toast({
            title: "Please select an AI voice type",
        })
        return setIsGenerating(false);
    }

    try {
      // Send the Eleven Labs voice ID and prompt text
      const response = await getPodcastAudio({
        voice: voiceType, // This holds the Eleven Labs voice ID
        input: voicePrompt // This holds the text to convert to speech
      })

      // The action returns an ArrayBuffer, so we create a Blob from it
      const blob = new Blob([response], { type: 'audio/mpeg' });
      const fileName = `podcast-${uuidv4()}.mp3`;
      const file = new File([blob], fileName, { type: 'audio/mpeg' });

      const uploaded = await startUpload([file]);
      const storageId = (uploaded[0].response as any).storageId;

      setAudioStorageId(storageId);
 
      const audioUrl = await getAudioUrl({ storageId });
      setAudio(audioUrl!);
      setIsGenerating(false);
      toast({
         title: "Podcast generated successfully",
      })
   } catch (error) {
      console.error('Error generating podcast', error)
        toast({
          title: "Error creating a podcast",
          variant: 'destructive',
          description: `Check console for details (Error: ${error instanceof Error ? error.message : 'Unknown Error'})`
        })
       setIsGenerating(false);
   }

  }

  return { isGenerating, generatePodcast }
}

const GeneratePodcast = (props: GeneratePodcastProps) => {
  const { isGenerating, generatePodcast } = useGenerateElevenLabsAudio(props);

  return (
    <div>
      <div className="flex flex-col gap-2.5 w-full">
        <Label className="text-16 font-bold text-white-1">
          AI Prompt to generate Podcast
        </Label>
        <Textarea 
          className="input-class font-light focus-visible:ring-offset-orange-1"
          placeholder='Provide text to generate audio'
          rows={5}
          value={props.voicePrompt}
          onChange={(e) => props.setVoicePrompt(e.target.value)}
        />
      </div>
      <div className="mt-5 w-full max-w-[200px]">
      <Button 
          type="button" // Change to type="button" to prevent form submission
          className="text-16 bg-orange-1 py-4 font-bold text-white-1" 
          onClick={generatePodcast}
          disabled={isGenerating || !props.voiceType || !props.voicePrompt}
        >
        {isGenerating ? (
          <>
          Generating
            <Loader size={20} className="animate-spin ml-2" />
          </>
        ) : (
          'Generate Podcast'
        )}
      </Button>
      </div>
      {props.audio && (
        <audio 
          controls
          src={props.audio}
          autoPlay
          className="mt-5"
          onLoadedMetadata={(e) => props.setAudioDuration(e.currentTarget.duration)}
        />
      )}
    </div>
  )
}

export default GeneratePodcast