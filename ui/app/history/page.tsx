"use client";

import { useEffect, useState } from "react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { CopyField } from "../../components/ui/copy-field";
import { FavouriteButton } from "../../components/ui/button";
import { 
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "../../components/ui/alert-dialog";
import { History, Heart, Calendar, User, BookOpen, Image, Copy, ChevronDown, ChevronUp, Search, Trash2, Filter, AlertTriangle, Brain, Hash } from "lucide-react";
import { toast } from "sonner";
import { ProtectedRoute } from '../../components/ProtectedRoute';
import { useAuth } from '@/lib/auth';

interface HistoryRecord {
  id: number;
  timestamp: string;
  storyPrompt: string;
  character: string | null;
  story: string;
  imagePrompt: string;
  favourite?: boolean;
  modelName?: string;
  inputTokens?: number;
  outputTokens?: number;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [favourites, setFavourites] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'all' | 'favourites'>('all');
  const [sort, setSort] = useState<'desc' | 'asc' | 'model'>('desc');
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredRecords, setFilteredRecords] = useState<HistoryRecord[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; prompt: string } | null>(null);

  const fetchHistory = async (sort: 'desc' | 'asc' | 'model' = 'desc') => {
    setLoading(true);
    const res = await fetch(`http://localhost:8000/history?sort=${sort}`);
    const data = await res.json();
    setHistory(Array.isArray(data.history) ? data.history : []);
    setLoading(false);
  };

  const fetchFavourites = async () => {
    setLoading(true);
    const res = await fetch(`http://localhost:8000/favourites`);
    const data = await res.json();
    setFavourites(Array.isArray(data.favourites) ? data.favourites : []);
    setLoading(false);
  };

  useEffect(() => {
    if (tab === 'all') fetchHistory(sort);
    else fetchFavourites();
    // eslint-disable-next-line
  }, [tab, sort]);

  // Filter records based on search query
  useEffect(() => {
    const records = tab === 'all' ? history : favourites;
    if (searchQuery.trim() === '') {
      setFilteredRecords(records);
    } else {
      const filtered = records.filter(record => 
        record.storyPrompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
        record.story.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (record.character && record.character.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setFilteredRecords(filtered);
    }
  }, [searchQuery, history, favourites, tab]);

  const handleToggleFavourite = async (id: number) => {
    await fetch(`http://localhost:8000/history/${id}/favourite`, { method: 'POST' });
    if (tab === 'all') fetchHistory(sort);
    else fetchFavourites();
  };

  const openDeleteDialog = (id: number, prompt: string) => {
    setDeleteTarget({ id, prompt });
    setDeleteDialogOpen(true);
  };

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setDeleteTarget(null);
  };

  const handleDeleteRecord = async () => {
    if (!deleteTarget) return;
    
    try {
      const response = await fetch(`http://localhost:8000/history/${deleteTarget.id}`, { method: 'DELETE' });
      if (response.ok) {
        toast.success('Story deleted successfully!');
        if (tab === 'all') fetchHistory(sort);
        else fetchFavourites();
        // Remove from expanded items if it was expanded
        const newExpanded = new Set(expandedItems);
        newExpanded.delete(deleteTarget.id);
        setExpandedItems(newExpanded);
      } else {
        toast.error('Failed to delete story');
      }
    } catch (error) {
      toast.error('Failed to delete story');
    }
    
    closeDeleteDialog();
  };

  const toggleExpanded = (id: number) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedItems(newExpanded);
  };

  const records = filteredRecords;

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
        <div className="container mx-auto px-4 py-6">
          {/* Compact Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-black text-techno mb-1">History</h1>
              <p className="text-sm text-techno/60">Your AI storytelling journey</p>
            </div>
            <div className="hidden sm:flex items-center gap-2 glass px-3 py-1.5 rounded-full border border-white/30">
              <History className="w-3 h-3 text-purple-500" />
              <span className="text-xs font-medium text-techno">{records.length} Stories</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-col gap-3 mb-6">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex gap-2">
                <Button
                  variant={tab === 'all' ? 'gold' : 'outline'}
                  size="sm"
                  onClick={() => setTab('all')}
                  className="h-8 px-3 text-xs"
                >
                  <BookOpen className="w-3 h-3 mr-1.5" />
                  All
                </Button>
                <Button
                  variant={tab === 'favourites' ? 'gold' : 'outline'}
                  size="sm"
                  onClick={() => setTab('favourites')}
                  className="h-8 px-3 text-xs"
                >
                  <Heart className="w-3 h-3 mr-1.5" />
                  Favourites
                </Button>
              </div>
              
              <div className="flex items-center gap-2 ml-auto">
                <span className="text-xs text-techno/60 font-medium">Sort by:</span>
                <select
                  className="h-8 text-xs rounded-lg border border-white/30 bg-white/50 px-2 focus:border-gold/50 focus:outline-none"
                  value={sort}
                  onChange={e => setSort(e.target.value as any)}
                  disabled={tab === 'favourites'}
                >
                  <option value="desc">Date Desc</option>
                  <option value="asc">Date Asc</option>
                  <option value="model">Model</option>
                </select>
              </div>
            </div>
            
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-techno/40" />
              <input
                type="text"
                placeholder="Search stories, prompts, or characters..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-9 pl-10 pr-4 text-sm rounded-lg border-2 border-techno/20 bg-white/70 focus:border-gold/60 focus:outline-none placeholder:text-techno/40 shadow-sm"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-techno/40 hover:text-techno/60"
                >
                  ×
                </button>
              )}
            </div>
          </div>

          {/* Content */}
          {loading ? (
            <Card className="glass border-white/30">
              <CardContent className="flex items-center justify-center py-12">
                <div className="flex items-center gap-2 text-techno/60">
                  <div className="w-4 h-4 border-2 border-techno/30 border-t-techno rounded-full animate-spin"></div>
                  Loading...
                </div>
              </CardContent>
            </Card>
          ) : records.length === 0 ? (
            <Card className="glass border-white/30">
              <CardContent className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500/20 to-purple-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  {searchQuery ? <Search className="w-8 h-8 text-purple-500" /> : tab === 'favourites' ? <Heart className="w-8 h-8 text-purple-500" /> : <History className="w-8 h-8 text-purple-500" />}
                </div>
                <h3 className="text-lg font-semibold text-techno mb-2">
                  {searchQuery ? 'No Results Found' : `No ${tab === 'favourites' ? 'Favourites' : 'History'} Yet`}
                </h3>
                <p className="text-sm text-techno/60 max-w-xs mx-auto">
                  {searchQuery 
                    ? 'Try adjusting your search terms or clear the search to see all stories'
                    : tab === 'favourites' 
                      ? 'Stories you favourite will appear here for easy access'
                      : 'Your generated stories will appear here'
                  }
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {records.map((record) => {
                const isExpanded = expandedItems.has(record.id);
                return (
                  <Card key={record.id} className="glass border-white/30 hover:border-gold/30 transition-all duration-200 bg-gradient-to-r from-white/40 via-white/20 to-white/40">
                    <CardHeader 
                      className="pb-1 pt-2 px-3 cursor-pointer"
                      onClick={() => toggleExpanded(record.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-xs font-medium text-techno mb-0.5 truncate pr-4">
                            {searchQuery ? (
                              <span dangerouslySetInnerHTML={{
                                __html: record.storyPrompt.replace(
                                  new RegExp(`(${searchQuery})`, 'gi'),
                                  '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>'
                                )
                              }} />
                            ) : (
                              record.storyPrompt
                            )}
                          </CardTitle>
                          <div className="flex items-center gap-2">
                            <div className="flex items-center gap-1 text-xs text-techno/70">
                              <Calendar className="w-2.5 h-2.5" />
                              {new Date(record.timestamp).toLocaleDateString()}
                            </div>
                            {record.character && (
                              <Badge variant="default" className="bg-techno/10 text-techno px-1.5 py-0 text-xs rounded-sm border-techno/20">
                                <User className="w-2.5 h-2.5 mr-1" />
                                {record.character}
                              </Badge>
                            )}
                            {record.modelName && (
                              <Badge variant="default" className="bg-purple-50 text-purple-700 px-1.5 py-0 text-xs rounded-sm border-purple-200">
                                <Brain className="w-2.5 h-2.5 mr-1" />
                                {record.modelName}
                              </Badge>
                            )}
                            {(record.inputTokens !== undefined && record.outputTokens !== undefined) && (
                              <Badge variant="default" className="bg-green-50 text-green-700 px-1.5 py-0 text-xs rounded-sm border-green-200">
                                <Hash className="w-2.5 h-2.5 mr-1" />
                                {record.inputTokens + record.outputTokens} tokens
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <button
                            onClick={(e: React.MouseEvent) => {
                              e.stopPropagation();
                              openDeleteDialog(record.id, record.storyPrompt);
                            }}
                            className="p-1 rounded-md hover:bg-red-100 text-red-500 hover:text-red-600 transition-colors"
                            title="Delete story"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                          <div onClick={(e: React.MouseEvent) => {
                            e.stopPropagation();
                            handleToggleFavourite(record.id);
                          }}>
                            <FavouriteButton
                              isFavourited={!!record.favourite}
                              onClick={() => {}}
                            />
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="w-3.5 h-3.5 text-techno/40" />
                          ) : (
                            <ChevronDown className="w-3.5 h-3.5 text-techno/40" />
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    
                    {isExpanded && (
                      <CardContent className="pt-0 pb-2 px-3 border-t border-white/20">
                        <div className="space-y-2">
                          <div>
                            <div className="flex items-center gap-1 mb-1.5">
                              <BookOpen className="w-3 h-3 text-blue-500" />
                              <span className="text-xs font-medium text-techno">Generated Story</span>
                              <button
                                onClick={() => {
                                  navigator.clipboard.writeText(record.story);
                                  toast.success('Story copied to clipboard!');
                                }}
                                className="ml-auto text-xs text-gold hover:text-gold/80 font-medium flex items-center gap-0.5"
                              >
                                <Copy className="w-2.5 h-2.5" />
                                Copy
                              </button>
                            </div>
                            <div className="bg-white/50 rounded-md p-2 text-xs text-techno/80 max-h-32 overflow-y-auto">
                              {record.story.split(/\n\s*\n/).map((para, idx) => (
                                <p key={idx} className="mb-1.5 last:mb-0 leading-relaxed">
                                  {searchQuery ? (
                                    <span dangerouslySetInnerHTML={{
                                      __html: para.trim().replace(
                                        new RegExp(`(${searchQuery})`, 'gi'),
                                        '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>'
                                      )
                                    }} />
                                  ) : (
                                    para.trim()
                                  )}
                                </p>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <div className="flex items-center gap-1 mb-1.5">
                              <Image className="w-3 h-3 text-purple-500" />
                              <span className="text-xs font-medium text-techno">Image Prompt</span>
                              <button
                                onClick={() => {
                                  navigator.clipboard.writeText(record.imagePrompt);
                                  toast.success('Image prompt copied to clipboard!');
                                }}
                                className="ml-auto text-xs text-gold hover:text-gold/80 font-medium flex items-center gap-0.5"
                              >
                                <Copy className="w-2.5 h-2.5" />
                                Copy
                              </button>
                            </div>
                            <div className="bg-white/50 rounded-md p-2 text-xs text-techno/80">
                              {searchQuery ? (
                                <span dangerouslySetInnerHTML={{
                                  __html: record.imagePrompt.replace(
                                    new RegExp(`(${searchQuery})`, 'gi'),
                                    '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>'
                                  )
                                }} />
                              ) : (
                                record.imagePrompt
                              )}
                            </div>
                          </div>

                          {/* Token Usage Details */}
                          {(record.inputTokens !== undefined && record.outputTokens !== undefined) && (
                            <div className="space-y-1">
                              <span className="text-xs font-medium text-techno/80 flex items-center gap-1">
                                <Hash className="w-3 h-3 text-green-500" />
                                Token Usage
                              </span>
                              <div className="flex gap-2 text-xs">
                                <div className="bg-blue-50 px-2 py-1 rounded border border-blue-200">
                                  <span className="text-blue-700 font-medium">Input: {record.inputTokens}</span>
                                </div>
                                <div className="bg-orange-50 px-2 py-1 rounded border border-orange-200">
                                  <span className="text-orange-700 font-medium">Output: {record.outputTokens}</span>
                                </div>
                                <div className="bg-green-50 px-2 py-1 rounded border border-green-200">
                                  <span className="text-green-700 font-medium">Total: {record.inputTokens + record.outputTokens}</span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    )}
                  </Card>
                );
              })}
            </div>
          )}

          {/* Delete Confirmation Dialog */}
          <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <AlertDialogContent className="glass max-w-md border-white/30">
              <AlertDialogHeader>
                <AlertDialogTitle className="text-red-600 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Delete Story
                </AlertDialogTitle>
                <AlertDialogDescription className="text-techno/80 text-sm text-left">
                  Are you sure you want to delete this story?
                  {deleteTarget && (
                    <div className="mt-2 p-2 bg-red-50 rounded-md border border-red-200">
                      <p className="font-medium text-red-800 text-xs">
                        "{deleteTarget.prompt.length > 60 ? deleteTarget.prompt.substring(0, 60) + '...' : deleteTarget.prompt}"
                      </p>
                    </div>
                  )}
                  <p className="mt-2 text-red-600 font-medium">This action cannot be undone.</p>
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter className="gap-2">
                <AlertDialogCancel 
                  onClick={closeDeleteDialog}
                  className="h-9 text-sm flex-1"
                >
                  Cancel
                </AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteRecord}
                  className="h-9 text-sm flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  Delete Story
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </main>
    </ProtectedRoute>
  );
} 