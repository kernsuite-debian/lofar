/*
 * WaveformSettingsInputPanel.java
 *
 * Copyright (C) 2006
 * ASTRON (Netherlands Foundation for Research in Astronomy)
 * P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * $Id$
 */

package nl.astron.lofar.java.sas.otb.rsp.subbandstats;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JPanel;
import javax.swing.event.EventListenerList;

/**
 * The input panel for the WaveformSettingsPanel.
 *
 * @author  balken
 */
public class WaveformSettingsInputPanel extends JPanel implements ActionListener
{
    /** Used to store the listeners to this class */
    private EventListenerList listenerList;
    
    /** 
     * Creates new form WaveformSettingsInputPanel.
     */
    public WaveformSettingsInputPanel() 
    {
        listenerList = new EventListenerList();
        
        initComponents();
        
        btnSubmit.addActionListener(this);
    }
    
    /**
     * Returns the value of the mode textfield.
     */
    public String getPhase()
    {
        return txtPhase.getText();
    }
    
    /**
     * Returns the value of the frequency textfield.
     */
    public String getFrequency()
    {
        return txtFrequency.getText();
    }
    
    /**
     * Returns the value of the amplitude textfield.
     */
    public String getAmplitude()
    {
        return txtAmplitude.getText();
    }
    
    /**
     * Enables or disables the buttons on this panel.
     * @param   b       Boolean value used to determine to enable (true) or
     *                  disable (false).
     */
    public void enablePanel(boolean b) {
        /*
         * Only executed when the panel is to be disabled.
         * ( enablePanel ( false ) )
         */
        if (!b) {
            txtPhase.setText("");
            txtFrequency.setText("");
            txtAmplitude.setText("");
        }
        
        txtPhase.setEnabled(b);
        txtFrequency.setEnabled(b);
        txtAmplitude.setEnabled(b);        
        btnSubmit.setEnabled(b);
    }
        
    /**
     * Invoked when a action occurs; when btnSubmit is pressed.
     */
    public void actionPerformed(ActionEvent e)
    {
        fireActionPerformed(e);
    }
    
    /**
     * Adds listener to the listeners list.
     */
    public void addActionListener(ActionListener l)
    {
        listenerList.add(ActionListener.class, l);
    }
    
    /**
     * Removes listener from the listeners list.
     */
    public void removeActionListener(ActionListener l)
    {
        listenerList.remove(ActionListener.class, l);
    }
    
    /**
     * Notify all listeners that a action had been performed.
     */
    public void fireActionPerformed(ActionEvent e) 
    {
            // Guaranteed to return a non-null array
            Object[] listeners = listenerList.getListenerList();
    
            // Process the listeners last to first, notifying
            // those that are interested in this event
            for (int i = listeners.length-2; i>=0; i-=2) 
            {
                    if (listeners[i]==ActionListener.class) 
                    {
                            ((ActionListener)listeners[i+1]).actionPerformed(e);
                    }
            }
    }
        
    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    // <editor-fold defaultstate="collapsed" desc=" Generated Code ">//GEN-BEGIN:initComponents
    private void initComponents() {
        lblPhase = new javax.swing.JLabel();
        lblFrequency = new javax.swing.JLabel();
        lblAmplitude = new javax.swing.JLabel();
        txtFrequency = new javax.swing.JTextField();
        txtPhase = new javax.swing.JTextField();
        txtAmplitude = new javax.swing.JTextField();
        btnSubmit = new javax.swing.JButton();
        jLabel1 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        jLabel3 = new javax.swing.JLabel();

        setBorder(javax.swing.BorderFactory.createTitledBorder("Input"));
        lblPhase.setText("Phase");

        lblFrequency.setText("Frequency");

        lblAmplitude.setText("Amplitude");

        btnSubmit.setText("OK");

        jLabel1.setFont(new java.awt.Font("Dialog", 0, 12));
        jLabel1.setText("(0-80 Mhz)");

        jLabel2.setFont(new java.awt.Font("Dialog", 0, 12));
        jLabel2.setText("(0-360 \u00b0)");

        jLabel3.setFont(new java.awt.Font("Dialog", 0, 12));
        jLabel3.setText("(0-100 %)");

        org.jdesktop.layout.GroupLayout layout = new org.jdesktop.layout.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(layout.createSequentialGroup()
                .add(31, 31, 31)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.TRAILING)
                    .add(lblAmplitude)
                    .add(lblPhase)
                    .add(lblFrequency))
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(layout.createSequentialGroup()
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.TRAILING)
                            .add(txtFrequency, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 97, Short.MAX_VALUE)
                            .add(txtPhase, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 97, Short.MAX_VALUE)
                            .add(txtAmplitude, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 97, Short.MAX_VALUE))
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.TRAILING, false)
                            .add(jLabel3, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .add(jLabel2, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .add(jLabel1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                    .add(org.jdesktop.layout.GroupLayout.TRAILING, layout.createSequentialGroup()
                        .add(135, 135, 135)
                        .add(btnSubmit)))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(layout.createSequentialGroup()
                .addContainerGap()
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(txtFrequency, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                    .add(jLabel1)
                    .add(lblFrequency))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(txtPhase, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                    .add(jLabel2)
                    .add(lblPhase))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(lblAmplitude)
                    .add(txtAmplitude, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                    .add(jLabel3))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(btnSubmit)
                .addContainerGap(18, Short.MAX_VALUE))
        );
    }// </editor-fold>//GEN-END:initComponents

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnSubmit;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel lblAmplitude;
    private javax.swing.JLabel lblFrequency;
    private javax.swing.JLabel lblPhase;
    private javax.swing.JTextField txtAmplitude;
    private javax.swing.JTextField txtFrequency;
    private javax.swing.JTextField txtPhase;
    // End of variables declaration//GEN-END:variables
}