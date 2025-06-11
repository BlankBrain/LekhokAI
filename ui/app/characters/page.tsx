'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { Users, Plus, Edit, Trash2, Calendar, BarChart3, Clock, FileText, Upload, Eye } from 'lucide-react';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import { useAuth } from '@/lib/auth';

interface Character {
  name: string;
  created_at?: string;
  usage_count?: number;
  last_used?: string;
  config?: string;
}

export default function CharactersPage() {
  const { user } = useAuth();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [config, setConfig] = useState('');
  const [newCharacterId, setNewCharacterId] = useState('');
  const [newCharacterName, setNewCharacterName] = useState('');
  const [addMode, setAddMode] = useState<'form' | 'yaml'>('form');
  const [formFields, setFormFields] = useState({
    id: '',
    name: '',
    description: '',
    traits: '',
    style: '',
  });
  const [personaFile, setPersonaFile] = useState<File | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [deleteCountdown, setDeleteCountdown] = useState(5);
  const countdownRef = useRef<NodeJS.Timeout | null>(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Session-Token': token || ''
    };
  };

  useEffect(() => {
    fetchCharacters();
  }, []);

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('auth_token');
      if (!token) {
        // No token available, set empty array and stop loading
        setCharacters([]);
        return;
      }

      const response = await fetch('http://localhost:8000/characters', {
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          // Unauthorized - clear characters and show as empty
          setCharacters([]);
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Safely extract characters data
      const charactersData = data?.characters || data || [];
      
      // Ensure we always set an array
      setCharacters(Array.isArray(charactersData) ? charactersData : []);
    } catch (error) {
      console.error('Error fetching characters:', error);
      // Set empty array on error to prevent undefined issues
      setCharacters([]);
      toast.error('Failed to load characters');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (character: Character) => {
    setSelectedCharacter(character);
    setConfig(character.config || '');
    setIsEditing(true);
  };

  const handleSave = async () => {
    if (!selectedCharacter) return;

    try {
      const response = await fetch(`http://localhost:8000/characters/${selectedCharacter.name}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ config }),
      });

      if (response.ok) {
        setIsEditing(false);
        fetchCharacters();
        toast.success('Character updated successfully!');
      }
    } catch (error) {
      console.error('Error saving character:', error);
      toast.error('Failed to save character');
    }
  };

  const handleDelete = async (characterName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/characters/${characterName}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        fetchCharacters();
        toast.success('Character deleted successfully!');
      }
    } catch (error) {
      console.error('Error deleting character:', error);
      toast.error('Failed to delete character');
    }
  };

  const generateYamlFromForm = () => {
    const { name, description, traits, style } = formFields;
    return [
      `name: "${name}"`,
      `description: "${description}"`,
      `traits:`,
      ...traits.split(',').map(t => `  - ${t.trim()}`),
      `style:`,
      ...style.split(',').map(s => `  - ${s.trim()}`),
    ].join('\n');
  };

  const openDeleteDialog = (characterName: string) => {
    setDeleteTarget(characterName);
    setDeleteCountdown(5);
    setDeleteDialogOpen(true);
    if (countdownRef.current) clearInterval(countdownRef.current);
    countdownRef.current = setInterval(() => {
      setDeleteCountdown((prev) => {
        if (prev <= 1) {
          if (countdownRef.current) clearInterval(countdownRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setDeleteTarget(null);
    setDeleteCountdown(5);
    if (countdownRef.current) clearInterval(countdownRef.current);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    await handleDelete(deleteTarget);
    closeDeleteDialog();
  };

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-gold/5">
        <div className="container mx-auto px-4 py-6">
          {/* Compact Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-black text-techno mb-1">Characters</h1>
              <p className="text-sm text-techno/60">Manage your AI storytelling personas</p>
            </div>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="gold" size="sm" className="h-9 px-4">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Character
                </Button>
              </DialogTrigger>
              <DialogContent className="glass max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-techno flex items-center gap-2">
                    <Users className="w-5 h-5 text-gold" />
                    Add New Character
                  </DialogTitle>
                </DialogHeader>
                <Tabs defaultValue="form" className="w-full" onValueChange={v => setAddMode(v as 'form' | 'yaml')}>
                  <TabsList className="mb-4">
                    <TabsTrigger value="form" className="text-xs">Form</TabsTrigger>
                    <TabsTrigger value="yaml" className="text-xs">YAML</TabsTrigger>
                  </TabsList>
                  <TabsContent value="form" className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <input
                        type="text"
                        placeholder="Character ID (e.g. himu)"
                        value={formFields.id}
                        onChange={e => setFormFields(f => ({ ...f, id: e.target.value }))}
                        className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                      />
                      <input
                        type="text"
                        placeholder="Character Name (e.g. হিমু)"
                        value={formFields.name}
                        onChange={e => setFormFields(f => ({ ...f, name: e.target.value }))}
                        className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                      />
                    </div>
                    <input
                      type="text"
                      placeholder="Description"
                      value={formFields.description}
                      onChange={e => setFormFields(f => ({ ...f, description: e.target.value }))}
                      className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                    />
                    <input
                      type="text"
                      placeholder="Traits (comma separated)"
                      value={formFields.traits}
                      onChange={e => setFormFields(f => ({ ...f, traits: e.target.value }))}
                      className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                    />
                    <input
                      type="text"
                      placeholder="Style (comma separated)"
                      value={formFields.style}
                      onChange={e => setFormFields(f => ({ ...f, style: e.target.value }))}
                      className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                    />
                    <div>
                      <label className="block text-techno/70 mb-2 text-sm font-medium flex items-center gap-1.5">
                        <Upload className="w-3 h-3" />
                        Persona File (Required)
                      </label>
                      <input
                        type="file"
                        accept=".txt"
                        onChange={e => setPersonaFile(e.target.files?.[0] || null)}
                        className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-techno/70 mb-2 text-sm font-medium flex items-center gap-1.5">
                        <Eye className="w-3 h-3" />
                        YAML Preview
                      </label>
                      <pre className="bg-white/50 rounded-lg p-3 text-xs font-mono border border-white/20 text-techno/80 whitespace-pre-wrap max-h-32 overflow-y-auto">{generateYamlFromForm()}</pre>
                    </div>
                  </TabsContent>
                  <TabsContent value="yaml" className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <input
                        type="text"
                        placeholder="Character ID (e.g. himu)"
                        value={newCharacterId}
                        onChange={e => setNewCharacterId(e.target.value)}
                        className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                      />
                      <input
                        type="text"
                        placeholder="Character Name (e.g. হিমু)"
                        value={newCharacterName}
                        onChange={e => setNewCharacterName(e.target.value)}
                        className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                      />
                    </div>
                    <Textarea
                      placeholder="Enter character YAML configuration..."
                      value={config}
                      onChange={(e) => setConfig(e.target.value)}
                      className="min-h-[200px] font-mono text-sm"
                    />
                    <div>
                      <label className="block text-techno/70 mb-2 text-sm font-medium flex items-center gap-1.5">
                        <Upload className="w-3 h-3" />
                        Persona File (Required)
                      </label>
                      <input
                        type="file"
                        accept=".txt"
                        onChange={e => setPersonaFile(e.target.files?.[0] || null)}
                        className="w-full rounded-lg border border-white/30 bg-white/50 px-3 py-2 text-sm focus:border-gold/50 focus:outline-none"
                      />
                    </div>
                  </TabsContent>
                </Tabs>
                <Button variant="gold" size="sm" className="w-full h-9" onClick={async () => {
                  let id = '';
                  let name = '';
                  let yaml = '';
                  if (addMode === 'form') {
                    id = formFields.id.trim();
                    name = formFields.name.trim();
                    yaml = generateYamlFromForm();
                  } else {
                    id = newCharacterId.trim();
                    name = newCharacterName.trim();
                    yaml = config.trim();
                  }
                  if (!id || !name || !yaml || !personaFile) {
                    toast.error('Please provide all required fields and persona file.');
                    return;
                  }
                  try {
                    const formData = new FormData();
                    formData.append('character', id);
                    formData.append('name', name);
                    formData.append('config', yaml);
                    formData.append('persona_file', personaFile);

                    const response = await fetch('http://localhost:8000/characters', {
                      method: 'POST',
                      headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
                        'X-Session-Token': localStorage.getItem('auth_token') || ''
                      },
                      body: formData,
                    });
                    if (response.ok) {
                      setNewCharacterId('');
                      setNewCharacterName('');
                      setConfig('');
                      setFormFields({ id: '', name: '', description: '', traits: '', style: '' });
                      setPersonaFile(null);
                      fetchCharacters();
                      toast.success('Character added successfully!');
                      const closeBtn = document.querySelector('[data-state="open"] [data-dismiss]');
                      if (closeBtn) (closeBtn as HTMLElement).click();
                      else setIsEditing(false);
                    } else {
                      const error = await response.json();
                      toast.error(error.detail || 'Failed to add character.');
                    }
                  } catch (error) {
                    toast.error('Failed to add character.');
                  }
                }}>
                  <Plus className="w-4 h-4 mr-2" />
                  Save Character
                </Button>
              </DialogContent>
            </Dialog>
          </div>

          {/* Characters Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {loading ? (
              <Card className="glass border-white/30 col-span-full flex items-center justify-center py-12">
                <CardContent className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500/20 to-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Users className="w-8 h-8 text-blue-500" />
                  </div>
                  <h3 className="text-lg font-semibold text-techno mb-2">Loading...</h3>
                  <p className="text-sm text-techno/60 mb-4 max-w-xs">
                    Please wait while we load your characters
                  </p>
                </CardContent>
              </Card>
            ) : characters.length === 0 ? (
              <Card className="glass border-white/30 col-span-full flex items-center justify-center py-12">
                <CardContent className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500/20 to-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Users className="w-8 h-8 text-blue-500" />
                  </div>
                  <h3 className="text-lg font-semibold text-techno mb-2">No Characters Yet</h3>
                  <p className="text-sm text-techno/60 mb-4 max-w-xs">
                    Create your first AI character to start generating personalized stories
                  </p>
                </CardContent>
              </Card>
            ) : (
              characters.map((character) => (
                <Card key={character.name} className="glass border-white/30 hover:border-gold/30 transition-all duration-200 group">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500/20 to-blue-500/10 rounded-lg flex items-center justify-center">
                          <Users className="w-4 h-4 text-blue-500" />
                        </div>
                        <span className="text-techno font-semibold truncate">{character.name}</span>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0 space-y-3">
                    <div className="grid grid-cols-1 gap-2 text-xs">
                      <div className="flex items-center gap-2 text-techno/70">
                        <Calendar className="w-3 h-3" />
                        <span>Added: {character.created_at ? new Date(character.created_at).toLocaleDateString() : 'Unknown'}</span>
                      </div>
                      <div className="flex items-center gap-2 text-techno/70">
                        <BarChart3 className="w-3 h-3" />
                        <span>Used: {character.usage_count ?? 0} times</span>
                      </div>
                      <div className="flex items-center gap-2 text-techno/70">
                        <Clock className="w-3 h-3" />
                        <span>Last: {character.last_used ? new Date(character.last_used).toLocaleDateString() : 'Never'}</span>
                      </div>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(character)}
                        className="flex-1 h-8 text-xs"
                      >
                        <Edit className="w-3 h-3 mr-1" />
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => openDeleteDialog(character.name)}
                        className="flex-1 h-8 text-xs"
                      >
                        <Trash2 className="w-3 h-3 mr-1" />
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Edit Dialog */}
          {isEditing && selectedCharacter && (
            <Dialog open={isEditing} onOpenChange={setIsEditing}>
              <DialogContent className="glass max-w-2xl">
                <DialogHeader>
                  <DialogTitle className="text-techno flex items-center gap-2">
                    <Edit className="w-5 h-5 text-gold" />
                    Edit Character: {selectedCharacter.name}
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="block text-techno/70 mb-2 text-sm font-medium flex items-center gap-1.5">
                      <FileText className="w-3 h-3" />
                      Configuration
                    </label>
                    <Textarea
                      value={config}
                      onChange={(e) => setConfig(e.target.value)}
                      className="min-h-[250px] font-mono text-sm"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setIsEditing(false)} className="flex-1 h-9 text-sm">
                      Cancel
                    </Button>
                    <Button variant="gold" onClick={handleSave} className="flex-1 h-9 text-sm">
                      Save Changes
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          )}

          {/* Delete Dialog */}
          <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <DialogContent className="glass max-w-md">
              <DialogHeader>
                <DialogTitle className="text-red-600 flex items-center gap-2">
                  <Trash2 className="w-5 h-5" />
                  Delete Character
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <p className="text-techno/80 text-sm">
                  Are you sure you want to delete <span className="font-bold">{deleteTarget}</span>? This action cannot be undone.
                </p>
                <div className="space-y-2">
                  <Button
                    variant="destructive"
                    disabled={deleteCountdown > 0}
                    onClick={confirmDelete}
                    className="w-full h-9 text-sm"
                  >
                    {deleteCountdown > 0 ? `Confirm Delete (${deleteCountdown}s)` : 'Confirm Delete'}
                  </Button>
                  <Button variant="outline" onClick={closeDeleteDialog} className="w-full h-9 text-sm">
                    Cancel
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </main>
    </ProtectedRoute>
  );
} 