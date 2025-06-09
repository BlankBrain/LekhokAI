'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { CopyField } from '@/components/ui/copy-field';
import { PenTool, Users, Settings, Clock, Sparkles, BookOpen, Zap } from 'lucide-react';

export default function Home() {
  const [recentHistory, setRecentHistory] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/history')
      .then(res => res.json())
      .then(data => setRecentHistory(Array.isArray(data.history) ? data.history.slice(0, 2) : []));
  }, []);

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-techno/5 to-gold/5"></div>
        <div className="container mx-auto px-4 py-16 relative">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 glass-card px-4 py-2 mb-6 rounded-full">
              <Sparkles className="w-4 h-4 text-gold" />
              <span className="text-sm font-medium text-techno">AI-Powered Storytelling</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight">
              <span className="text-techno">Create Amazing</span><br />
              <span className="bg-gradient-to-r from-gold to-yellow-400 bg-clip-text text-transparent">Stories</span>
            </h1>
            
            <p className="text-xl text-techno/70 mb-8 max-w-2xl mx-auto">
              Unleash your creativity with KarigorAI's character-driven storytelling engine. 
              Generate compelling narratives in seconds.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/generate">
                <Button size="lg" variant="gold" className="group h-12 px-8">
                  <PenTool className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" />
                  Start Creating
                </Button>
              </Link>
              <Link href="/characters">
                <Button size="lg" variant="outline" className="h-12 px-8 glass-border">
                  <Users className="w-5 h-5 mr-2" />
                  Explore Characters
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
          <Card className="glass group hover:shadow-xl hover:scale-105 transition-all duration-300 border-white/20">
            <CardHeader className="pb-3">
              <div className="w-12 h-12 bg-gradient-to-br from-gold/20 to-gold/10 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <PenTool className="w-6 h-6 text-gold" />
              </div>
              <CardTitle className="text-lg text-techno">Generate Stories</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-techno/70 mb-4">Create compelling narratives with AI-powered characters</p>
              <Link href="/generate">
                <Button variant="ghost" size="sm" className="w-full text-gold hover:bg-gold/10">
                  Start Writing <Zap className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="glass group hover:shadow-xl hover:scale-105 transition-all duration-300 border-white/20">
            <CardHeader className="pb-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-blue-500/10 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <Users className="w-6 h-6 text-blue-400" />
              </div>
              <CardTitle className="text-lg text-techno">Characters</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-techno/70 mb-4">Manage and customize your AI storytelling personas</p>
              <Link href="/characters">
                <Button variant="ghost" size="sm" className="w-full text-blue-400 hover:bg-blue-400/10">
                  Manage <Users className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="glass group hover:shadow-xl hover:scale-105 transition-all duration-300 border-white/20">
            <CardHeader className="pb-3">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500/20 to-purple-500/10 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <BookOpen className="w-6 h-6 text-purple-400" />
              </div>
              <CardTitle className="text-lg text-techno">History</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-techno/70 mb-4">Browse and manage your story collection</p>
              <Link href="/history">
                <Button variant="ghost" size="sm" className="w-full text-purple-400 hover:bg-purple-400/10">
                  Browse <Clock className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="glass group hover:shadow-xl hover:scale-105 transition-all duration-300 border-white/20">
            <CardHeader className="pb-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500/20 to-green-500/10 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <Settings className="w-6 h-6 text-green-400" />
              </div>
              <CardTitle className="text-lg text-techno">Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-techno/70 mb-4">Fine-tune AI parameters and preferences</p>
              <Link href="/settings">
                <Button variant="ghost" size="sm" className="w-full text-green-400 hover:bg-green-400/10">
                  Configure <Settings className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Recent Activity */}
      {recentHistory.length > 0 && (
        <section className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 bg-gradient-to-br from-gold/20 to-gold/10 rounded-lg flex items-center justify-center">
                <Clock className="w-4 h-4 text-gold" />
              </div>
              <h2 className="text-2xl font-bold text-techno">Recent Creations</h2>
            </div>
            
            <div className="grid gap-4">
              {recentHistory.map(record => (
                <Card key={record.id} className="glass border-white/20 hover:border-gold/30 transition-colors">
                  <CardHeader className="pb-3">
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2">
                      <div className="flex-1">
                        <CardTitle className="text-base font-semibold text-techno/90 line-clamp-2">
                          {record.storyPrompt}
                        </CardTitle>
                        {record.character && (
                          <div className="text-sm text-techno/70 mt-1">
                            <span className="inline-flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {record.character}
                            </span>
                          </div>
                        )}
                      </div>
                      <span className="text-xs text-techno/60 shrink-0">
                        {new Date(record.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <CopyField label="Story" value={record.story} />
                    <CopyField label="Image Prompt" value={record.imagePrompt} />
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <div className="text-center mt-6">
              <Link href="/history">
                <Button variant="outline" className="glass-border">
                  View All Stories <BookOpen className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </section>
      )}
    </main>
  );
} 