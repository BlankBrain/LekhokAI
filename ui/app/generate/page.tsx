'use client';

import { useState } from 'react';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Textarea } from '../../components/ui/textarea';
import { toast } from 'sonner';
import { CopyField } from '../../components/ui/copy-field';
import { FavouriteButton } from '../../components/ui/button';
import { PenTool, Sparkles, Users, Wand2, Heart, Copy, ImageIcon, AlertTriangle, Info, Wrench, Loader2 } from 'lucide-react';
import LoadingSpinner from '../../components/LoadingSpinner';
import SkeletonLoader, { CardSkeleton, ImageSkeleton } from '../../components/SkeletonLoader';
import ErrorBoundary from '../../components/ErrorBoundary';

interface Character {
  id: string;
  name: string;
}

export default function GeneratePage() {
  const [storyPrompt, setStoryPrompt] = useState('');
  const [selectedCharacter, setSelectedCharacter] = useState<string>('');
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedStory, setGeneratedStory] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [historyId, setHistoryId] = useState<number | null>(null);
  const [isFavourited, setIsFavourited] = useState(false);
  
  // Image generation states
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);

  // Fetch characters on component mount
  useState(() => {
    fetch('http://localhost:8000/characters')
      .then(res => res.json())
      .then(data => setCharacters(Array.isArray(data.characters) ? data.characters : []))
      .catch(err => toast.error('Failed to load characters'));
  });

  const handleGenerate = async () => {
    if (!storyPrompt.trim()) {
      toast.error('Please enter a story prompt');
      return;
    }

    if (!selectedCharacter) {
      toast.error('Please select a character');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          storyIdea: storyPrompt,
          character: selectedCharacter,
        }),
      });

      if (!response.ok) throw new Error('Failed to generate story');

      const data = await response.json();
      setGeneratedStory(data.story);
      setImagePrompt(data.imagePrompt);
      toast.success('Story generated successfully!');

      // Fetch the latest history record to get its id and favourite status
      const histRes = await fetch('http://localhost:8000/history?sort=desc');
      const histData = await histRes.json();
      if (Array.isArray(histData.history)) {
        // Find the most recent record matching the generated story and prompt
        const found = histData.history.find((rec: any) =>
          rec.storyPrompt === storyPrompt && rec.story === data.story
        );
        if (found) {
          setHistoryId(found.id);
          setIsFavourited(!!found.favourite);
        } else {
          setHistoryId(null);
          setIsFavourited(false);
        }
      }
    } catch (error) {
      toast.error('Failed to generate story');
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleToggleFavourite = async () => {
    if (!historyId) return;
    await fetch(`http://localhost:8000/history/${historyId}/favourite`, { method: 'POST' });
    // Refetch to get updated favourite status
    const histRes = await fetch('http://localhost:8000/history?sort=desc');
    const histData = await histRes.json();
    if (Array.isArray(histData.history)) {
      const found = histData.history.find((rec: any) => rec.id === historyId);
      setIsFavourited(!!(found && found.favourite));
    }
  };

  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) {
      toast.error('No image prompt available');
      return;
    }

    setIsGeneratingImage(true);
    setImageError(null);
    
    try {
      const response = await fetch('http://localhost:8000/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          imagePrompt: imagePrompt,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate image');
      }

      const data = await response.json();
      
      if (data.success) {
        setGeneratedImage(data.image_data);
        toast.success('Image generated successfully!');
      } else {
        throw new Error(data.error || 'Image generation failed');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to generate image';
      setImageError(errorMsg);
      toast.error(errorMsg);
      console.error('Image generation error:', error);
    } finally {
      setIsGeneratingImage(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
      <div className="container mx-auto px-4 py-6">
        {/* Compact Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-black text-techno mb-1">Generate Story</h1>
            <p className="text-sm text-techno/60">Transform ideas into compelling narratives</p>
          </div>
          <div className="hidden sm:flex items-center gap-2 glass px-3 py-1.5 rounded-full border border-white/30">
            <Sparkles className="w-3 h-3 text-gold" />
            <span className="text-xs font-medium text-techno">AI Powered</span>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Form Section */}
          <div className="space-y-4">
            <Card className="glass border-white/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2 text-techno">
                  <PenTool className="w-4 h-4 text-gold" />
                  Story Input
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-techno flex items-center gap-1.5">
                    <Wand2 className="w-3 h-3" />
                    Story Prompt
                    <span className="text-red-500 text-xs">*</span>
                  </label>
                  <Textarea
                    placeholder="Describe your story idea..."
                    value={storyPrompt}
                    onChange={(e) => setStoryPrompt(e.target.value)}
                    className="min-h-[100px] glass border-white/30 focus:border-gold/50 resize-none text-sm"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-techno flex items-center gap-1.5">
                    <Users className="w-3 h-3" />
                    Character
                    <span className="text-red-500 text-xs">*</span>
                  </label>
                  <select
                    value={selectedCharacter}
                    onChange={(e) => setSelectedCharacter(e.target.value)}
                    className={`w-full p-2.5 glass border rounded-lg focus:border-gold/50 focus:outline-none text-techno bg-white/50 text-sm ${
                      !selectedCharacter ? 'border-red-200' : 'border-white/30'
                    }`}
                  >
                    <option value="">Select a character...</option>
                    {characters.map((char) => (
                      <option key={char.id} value={char.id}>
                        {char.name}
                      </option>
                    ))}
                  </select>
                  {!selectedCharacter && (
                    <p className="text-xs text-red-500 flex items-center gap-1">
                      <span>Please select a character to continue</span>
                    </p>
                  )}
                </div>

                <Button 
                  onClick={handleGenerate} 
                  disabled={isGenerating || !storyPrompt.trim() || !selectedCharacter}
                  variant="gold"
                  className="w-full h-10 text-sm font-semibold"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Generate Story
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Image Generation Development Notice */}
            {imagePrompt && (
              <Card className="glass border-amber-200/60 bg-gradient-to-r from-amber-50/80 to-yellow-50/80">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2 text-amber-700">
                    <Wrench className="w-4 h-4 text-amber-600" />
                    Image Generation - Beta Feature
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div className="space-y-2">
                      <p className="text-xs text-amber-700 font-medium">
                        🚧 This feature is currently under development
                      </p>
                      <ul className="text-xs text-amber-600 space-y-1">
                        <li>• Image quality and accuracy may vary</li>
                        <li>• Generation times can be longer than expected</li>
                        <li>• Some prompts may not generate as intended</li>
                        <li>• Feature improvements are being actively developed</li>
                      </ul>
                      <div className="flex items-center gap-1 pt-1">
                        <Info className="w-3 h-3 text-amber-600" />
                        <span className="text-xs text-amber-600">We appreciate your patience as we refine this feature</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Image Prompt Card - Compact */}
            {imagePrompt && (
              <Card className="glass border-white/30">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm flex items-center gap-2 text-techno">
                      <ImageIcon className="w-3 h-3 text-purple-500" />
                      Image Prompt
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          const cleanedImagePrompt = imagePrompt.replace(/\*\*/g, '');
                          navigator.clipboard.writeText(cleanedImagePrompt);
                          toast.success('Image prompt copied!');
                        }}
                        className="text-xs text-gold hover:text-gold/80 font-medium flex items-center gap-1 px-2 py-1 rounded"
                      >
                        <Copy className="w-3 h-3" />
                        Copy
                      </button>
                      <Button
                        onClick={handleGenerateImage}
                        disabled={isGeneratingImage || !imagePrompt.trim()}
                        size="sm"
                        className="text-xs h-6 px-3 bg-purple-600 hover:bg-purple-700 text-white"
                      >
                        {isGeneratingImage ? (
                          <>
                            <div className="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin mr-1" />
                            Generating...
                          </>
                        ) : (
                          <>
                            <Wand2 className="w-3 h-3 mr-1" />
                            Generate
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="bg-white/50 rounded-lg p-3 text-xs text-techno/80 border border-white/30">
                    {imagePrompt.replace(/\*\*/g, '')}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Story Output Section */}
          <div className="lg:min-h-[600px]">
            {generatedStory ? (
              <Card className="glass border-white/30 h-full">
                <CardHeader className="pb-3 border-b border-white/20">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2 text-techno">
                      <PenTool className="w-4 h-4 text-gold" />
                      Generated Story
                    </CardTitle>
                    <div className="flex items-center gap-1">
                      {historyId && (
                        <button
                          onClick={handleToggleFavourite}
                          className={`p-1.5 rounded-md transition-all ${
                            isFavourited 
                              ? 'bg-red-100 text-red-600' 
                              : 'bg-white/50 text-techno/60 hover:text-red-500'
                          }`}
                        >
                          <Heart className={`w-3 h-3 ${isFavourited ? 'fill-current' : ''}`} />
                        </button>
                      )}
                      <button
                        onClick={() => {
                          const cleanedStory = generatedStory.replace(/\*\*/g, '');
                          navigator.clipboard.writeText(cleanedStory);
                          toast.success('Story copied!');
                        }}
                        className="bg-gold text-white px-3 py-1.5 rounded-md text-xs font-medium hover:bg-gold/90 transition-all flex items-center gap-1"
                      >
                        <Copy className="w-3 h-3" />
                        Copy
                      </button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-4 h-full overflow-y-auto">
                  <div className="space-y-3">
                    {generatedStory.split(/\n\s*\n/).map((para, idx) => (
                      <p key={idx} className="text-sm text-techno/90 leading-relaxed whitespace-pre-line">
                        {para.trim().replace(/\*\*/g, '')}
                      </p>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="glass border-white/30 h-full flex items-center justify-center">
                <CardContent className="text-center py-12">
                  <div className="w-16 h-16 bg-gradient-to-br from-gold/20 to-gold/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <PenTool className="w-8 h-8 text-gold" />
                  </div>
                  <h3 className="text-lg font-semibold text-techno mb-2">Ready to Create</h3>
                  <p className="text-sm text-techno/60 max-w-xs">
                    Enter your story idea and select a character to watch AI bring it to life
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Generated Image Section */}
        {(generatedImage || imageError || isGeneratingImage) && (
          <div className="mt-8">
            <Card className="glass border-white/30">
              <CardHeader className="pb-3 border-b border-white/20">
                <CardTitle className="text-lg flex items-center gap-2 text-techno">
                  <ImageIcon className="w-4 h-4 text-purple-500" />
                  Generated Image
                  <div className="flex items-center gap-1 ml-auto">
                    <span className="bg-amber-100 text-amber-700 text-xs px-2 py-1 rounded-full font-medium flex items-center gap-1">
                      <Wrench className="w-3 h-3" />
                      Beta
                    </span>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                {isGeneratingImage ? (
                  <div className="flex flex-col items-center justify-center h-64 space-y-4">
                    <div className="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
                    <p className="text-sm text-techno/60">Generating your image...</p>
                  </div>
                ) : imageError ? (
                  <div className="flex flex-col items-center justify-center h-64 space-y-4">
                    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                      <ImageIcon className="w-8 h-8 text-red-500" />
                    </div>
                    <div className="text-center">
                      <h3 className="text-lg font-semibold text-red-600 mb-2">Generation Failed</h3>
                      <p className="text-sm text-red-500">{imageError}</p>
                      <Button 
                        onClick={handleGenerateImage}
                        className="mt-3 bg-purple-600 hover:bg-purple-700 text-white"
                        size="sm"
                      >
                        Try Again
                      </Button>
                    </div>
                  </div>
                ) : generatedImage ? (
                  <div className="flex flex-col items-center space-y-4">
                    <div className="relative">
                      <div className="w-96 h-96 bg-white border-2 border-gray-200 rounded-lg overflow-hidden shadow-lg">
                        <img
                          src={`data:image/png;base64,${generatedImage}`}
                          alt="Generated from story"
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <button
                        onClick={() => {
                          // Create download link
                          const link = document.createElement('a');
                          link.href = `data:image/png;base64,${generatedImage}`;
                          link.download = `generated-image-${Date.now()}.png`;
                          link.click();
                        }}
                        className="absolute top-2 right-2 bg-white/90 hover:bg-white text-gray-700 p-2 rounded-lg shadow-md transition-all"
                        title="Download Image"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </button>
                    </div>
                    <p className="text-xs text-techno/60 text-center max-w-md">
                      Generated using AI • Click the download icon to save
                    </p>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </main>
  );
} 